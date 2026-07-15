"""
直接対戦成績
"""

import textwrap
from typing import TYPE_CHECKING, Any

import pandas as pd

import libs.global_value as g
from libs.functions.compose import text_item
from libs.types import CommandType, StyleOptions
from libs.utils import converter, dictutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.types import MessageType


def aggregation(m: "MessageParserProtocol") -> None:
    """
    直接対戦結果を集計して返す

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = CommandType.GAME_RESULTS
    g.params.guest_skip = g.params.guest_skip2

    # データ収集
    data: "MessageType"
    df_vs = g.params.read_data("SUMMARY_VERSUS_MATRIX", False)
    df_game = g.params.read_data("SUMMARY_DETAILS", False).fillna(value="")
    df_data = pd.DataFrame(columns=df_game.columns)  # ファイル出力用

    my_name = textutil.name_replace(g.params.player_name, add_mark=True)
    vs_list = [textutil.name_replace(x, add_mark=True) for x in g.params.competition_list]

    # 匿名化
    if g.params.anonymous:
        mapping_dict = textutil.anonymous_mapping([my_name] + vs_list)
        my_name = mapping_dict[my_name]
        vs_list = [mapping_dict[name] for name in vs_list]
        df_vs["my_name"] = df_vs["my_name"].replace(mapping_dict)
        df_vs["vs_name"] = df_vs["vs_name"].replace(mapping_dict)

    # 表示内容
    if g.params.all_player:
        vs = "全員"
    else:
        vs = ",".join(vs_list)

    game_result: dict[Any, Any] = {}  # 対戦結果格納用
    drop_name: list[str] = []  # 対戦記録なしプレイヤー

    if len(df_vs) == 0:  # 検索結果なし
        m.set_headline("対戦記録が見つかりません。", StyleOptions(title="直接対戦"))
        m.status.result = False
        return

    m.set_headline(tmpl_header(my_name, vs), StyleOptions(title="直接対戦"))
    for vs_name in vs_list:
        title = f"{my_name} vs {vs_name}"
        if vs_name in vs_list:
            data = df_vs.query("my_name == @my_name and vs_name == @vs_name")
            if data.empty:
                if len(vs_list) <= 5 and not g.params.all_player:
                    drop_name.append(vs_name)
                    game_result[title] = "対戦記録はありません。"
                continue

            game_result[title] = tmpl_vs_table(data.to_dict(orient="records")[0])

            # ゲーム結果
            if g.params.game_results:
                count = 0
                my_score = df_game.query("name == @my_name")
                vs_score = df_game.query("name == @vs_name")
                my_playtime = my_score["playtime"].to_list()
                vs_playtime = vs_score["playtime"].to_list()

                for playtime in sorted(set(my_playtime + vs_playtime)):
                    if playtime in my_playtime and playtime in vs_playtime:
                        current_game = df_game.query("playtime == @playtime")
                        df_data = current_game if df_data.empty else pd.concat([df_data, current_game])
                        count += 1
        else:  # 対戦記録なし
            game_result[title] = "\t対戦相手が見つかりません。\n\n"
    # 結果
    if len(game_result):
        for k, v in game_result.items():
            m.set_message(v, StyleOptions(title=k))
    else:
        m.set_message("対戦記録が見つかりません。", StyleOptions(title="対戦記録が見つかりません。", key_title=False))
        m.status.result = False
        return

    # ファイル出力
    if len(df_data):
        df_data["座席"] = df_data["seat"].apply(lambda x: ["東家", "南家", "西家", "北家"][x - 1])
        df_data["rpoint"] = df_data["rpoint"] * 100
        df_data = df_data.filter(items=["playtime", "座席", "name", "rank", "rpoint", "point", "yakuman"]).drop_duplicates()
        df_data.rename(columns=dictutil.rename_dicts(df_data.columns.to_list(), StyleOptions()), inplace=True)

    df_vs["対戦相手"] = df_vs["vs_name"].apply(lambda x: str(x).strip())
    df_vs["my_rpoint_avg"] = (df_vs["my_rpoint_avg"] * 100).astype("int")
    df_vs["vs_rpoint_avg"] = (df_vs["vs_rpoint_avg"] * 100).astype("int")
    df_vs.rename(columns=dictutil.rename_dicts(df_vs.columns.to_list(), StyleOptions()), inplace=True)
    df_vs2 = (
        df_vs.query("vs_name == @g.params.competition_list")
        .filter(
            items=[
                "対戦相手",
                "対戦結果",
                "勝率",
                "獲得ポイント(自分)",
                "平均ポイント(自分)",
                "平均素点(自分)",
                "順位分布(自分)",
                "平均順位(自分)",
                "獲得ポイント(相手)",
                "平均ポイント(相手)",
                "平均素点(相手)",
                "順位分布(相手)",
                "平均順位(相手)",
            ]
        )
        .drop_duplicates()
    )

    match g.params.format.lower():
        case "csv":
            m.set_message(converter.save_output(df_data, StyleOptions(format_type="csv", base_name="result")), StyleOptions(title="対戦結果"))
            m.set_message(converter.save_output(df_vs2, StyleOptions(format_type="csv", base_name="versus")), StyleOptions(title="成績"))
        case "text" | "txt":
            m.set_message(converter.save_output(df_data, StyleOptions(format_type="txt", base_name="result")), StyleOptions(title="対戦結果"))
            m.set_message(converter.save_output(df_vs2, StyleOptions(format_type="txt", base_name="versus")), StyleOptions(title="成績"))
        case _:
            pass


def tmpl_header(my_name: str, vs_name: str) -> str:
    """
    ヘッダテンプレート

    Args:
        my_name (str): 自分の名前
        vs_name (str): 相手の名前

    Returns:
        str: 出力データ

    """
    ret = textwrap.dedent(
        f"""\
        \tプレイヤー名：{my_name}
        \t対戦相手：{vs_name}
        \t集計範囲：{text_item.search_range()}
        \t{text_item.remarks(True)}
        """
    ).rstrip()

    return ret


def tmpl_vs_table(data: dict[Any, Any]) -> str:
    """
    直接対決結果表示テンプレート

    Args:
        data (dict[Any, Any]): 結果データ

    Returns:
        str: 出力データ

    """
    ret = textwrap.indent(
        "".join(
            [
                textwrap.dedent(
                    f"""\
                    対戦数：{data["game"]} 戦 {data["win"]} 勝 {data["lose"]} 敗 ({data["win%"]:.2f}%)
                    平均素点差：{(data["my_rpoint_avg"] - data["vs_rpoint_avg"]) * 100:+.0f} 点
                    獲得ポイント合計(自分)：{data["my_point_sum"]:+.1f}pt
                    獲得ポイント合計(相手)：{data["vs_point_sum"]:+.1f}pt
                    """.replace("-", "▲")
                ),
                textwrap.dedent(
                    f"""\
                    順位分布(自分)：{data["my_rank1"]}-{data["my_rank2"]}-{data["my_rank3"]}-{data["my_rank4"]} ({data["my_rank_avg"]:1.2f})
                    順位分布(相手)：{data["vs_rank1"]}-{data["vs_rank2"]}-{data["vs_rank3"]}-{data["vs_rank4"]} ({data["vs_rank_avg"]:1.2f})
                    """  # noqa: E501
                ),
            ]
        ),
        "\t",
    )

    return ret.rstrip() + "\n"
