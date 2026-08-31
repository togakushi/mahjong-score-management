"""
個人/チーム成績詳細
"""

import textwrap
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from table2ascii import Alignment, PresetStyle, table2ascii

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.domain.stats import StatsInfo
from libs.functions import badge, message
from libs.types import StyleOptions
from libs.utils import converter, dictutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.types import MessageType


def aggregation(m: "MessageParserProtocol") -> None:
    """
    成績詳細を集計

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.RECORD_DATA
    g.params.guest_skip = g.params.guest_skip2  # 検索動作を合わせる

    if (target_mode := g.params.target_mode) and target_mode != g.cfg.rule.get_mode(g.params.rule_version):
        m.set_headline(message.random_reply(m, "rule_mismatch"), StyleOptions(title="集計矛盾検出"))
        m.status.result = False
        return

    if g.params.player_name in g.cfg.team.lists:
        g.params.individual = False
    elif g.params.player_name in g.cfg.member.lists:
        g.params.individual = True

    # タイトル
    if g.params.individual:
        title = "個人成績詳細"
    else:
        title = "チーム成績詳細"

    # データ収集
    game_info = GameInfo()
    game_info.stats.read(g.params)
    header_text = message.header(game_info, m, indent=0)

    if not game_info.count or game_info.stats.result_df.empty or game_info.stats.record_df.empty:
        m.set_headline(header_text, StyleOptions(title=title))
        m.status.result = False
        return

    # 表示内容
    m.set_headline(
        "{header}\n\n{total}\n\n{rank_info}\n".format(
            header=header_text,
            rank_info=rank_information(game_info),
            total=totalization(game_info),
        ),
        StyleOptions(title=title, indent=1),
    )

    # 統計
    seat_data = pd.DataFrame(
        {  # 座席データ
            "席": ["東家", "南家", "西家", "北家"][: g.params.mode],
            "順位分布": game_info.stats.rank_distr_list2,
            "平均順位": [f"{x:.2f}".replace("0.00", "-.--") for x in game_info.stats.rank_avg_list],
            "トビ": game_info.stats.flying_list,
            "役満和了": game_info.stats.yakuman_list,
        }
    )
    if g.cfg.rule.get_draw_split(g.params.rule_version):
        seat_data.drop(columns=["順位分布"], inplace=True)

    if g.cfg.rule.get_draw_split(g.params.rule_version):
        balance_data = textwrap.dedent(
            f"""\
            全体：{game_info.stats.seat0.avg_balance("all"):+.1f}点
            """.replace("+0.0点", "記録なし")
        ).replace("-", "▲")
    else:
        if g.params.mode == 3:
            balance_data = textwrap.dedent(
                f"""\
                全体：{game_info.stats.seat0.avg_balance("all"):+.1f}点
                1着終了時：{game_info.stats.seat0.avg_balance("rank1"):+.1f}点
                2着終了時：{game_info.stats.seat0.avg_balance("rank2"):+.1f}点
                3着終了時：{game_info.stats.seat0.avg_balance("rank3"):+.1f}点
                """.replace("+0.0点", "記録なし")
            ).replace("-", "▲")
        else:
            balance_data = textwrap.dedent(
                f"""\
                全体：{game_info.stats.seat0.avg_balance("all"):+.1f}点
                連対時：{game_info.stats.seat0.avg_balance("top2"):+.1f}点
                逆連対時：{game_info.stats.seat0.avg_balance("lose2"):+.1f}点
                1着終了時：{game_info.stats.seat0.avg_balance("rank1"):+.1f}点
                2着終了時：{game_info.stats.seat0.avg_balance("rank2"):+.1f}点
                3着終了時：{game_info.stats.seat0.avg_balance("rank3"):+.1f}点
                4着終了時：{game_info.stats.seat0.avg_balance("rank4"):+.1f}点
                """.replace("+0.0点", "記録なし")
            ).replace("-", "▲")

    # 非表示項目
    seat_data.drop(
        columns=dictutil.dropitems_list(seat_data.columns.to_list()),
        inplace=True,
    )
    game_info.stats.result_df.drop(
        columns=dictutil.dropitems_list(game_info.stats.result_df.columns.to_list()),
        inplace=True,
    )
    game_info.stats.record_df.drop(
        columns=dictutil.dropitems_list(game_info.stats.record_df.columns.to_list()),
        inplace=True,
    )

    if g.params.statistics:
        m.set_message(df_to_seat_data(seat_data), StyleOptions(title="座席データ", indent=1))
        m.set_message(game_info.stats.seat0.best_record(), StyleOptions(title="ベストレコード", indent=1))
        m.set_message(game_info.stats.seat0.worst_record(), StyleOptions(title="ワーストレコード", indent=1))
        m.set_message(balance_data.strip(), StyleOptions(title="平均収支", indent=1))

    # レギュレーション
    remarks_df = g.params.read_data("REMARKS_INFO")
    count_df = remarks_df.groupby("matter").agg(matter_count=("matter", "count"), ex_total=("ex_point", "sum"), type=("type", "max"))
    count_df["matter"] = count_df.index

    if "役満和了" not in dictutil.dropitems_list():
        work_df = count_df.query("type == 0").filter(items=["matter", "matter_count"])
        m.set_message(work_df, StyleOptions(title="役満和了", indent=1, data_kind=StyleOptions.DataKind.REMARKS_YAKUMAN))

    if "卓外清算" not in dictutil.dropitems_list():
        if g.params.individual:
            work_df = count_df.query("type == 2").filter(items=["matter", "matter_count", "ex_total"])
        else:
            work_df = count_df.query("type == 2 or type == 3").filter(items=["matter", "matter_count", "ex_total"])
        m.set_message(work_df, StyleOptions(title="卓外清算", indent=1, data_kind=StyleOptions.DataKind.REMARKS_REGULATION))

    if "その他" not in dictutil.dropitems_list():
        work_df = count_df.query("type == 1").filter(items=["matter", "matter_count"])
        m.set_message(work_df, StyleOptions(title="その他", indent=1, data_kind=StyleOptions.DataKind.REMARKS_OTHER))

    # 対戦結果
    if g.params.versus:
        m.set_message(versus_data(), StyleOptions(title="対戦結果", indent=1))

    # 戦績
    if g.params.game_results:
        if g.params.verbose:
            m.set_message(
                results_details(),
                StyleOptions(title="戦績", data_kind=StyleOptions.DataKind.GAME_RESULTS_ALL, codeblock=False),
            )
        else:
            m.set_message(
                results_simple(),
                StyleOptions(title="戦績", data_kind=StyleOptions.DataKind.GAME_RESULTS, codeblock=False),
            )


def stats_list(m: "MessageParserProtocol") -> None:
    """
    成績詳細一覧表の生成

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.DETAILED_RESULTS
    g.params.guest_skip = g.params.guest_skip2

    if not g.params.player_list:
        if g.params.individual:
            g.params.player_list = g.cfg.member.lists
        else:
            g.params.player_list = g.cfg.team.lists
    if g.params.player_name in g.cfg.team.lists:
        g.params.update_from_dict({"individual": False})
    elif g.params.player_name in g.cfg.member.lists:
        g.params.update_from_dict({"individual": True})

    # データ収集
    data: "MessageType"
    game_info = GameInfo()

    # タイトル
    title = "成績詳細比較"
    m.set_headline(message.header(game_info, m, "", 1), StyleOptions(title=title))

    if not game_info.count:
        m.status.result = False
        return

    stats_df = pd.DataFrame()
    result_df = g.params.read_data("RESULTS_INFO")
    record_df = g.params.read_data("RECORD_INFO")
    rank_df = g.params.read_data("RANK_INFO")

    if g.params.anonymous:
        g.params.player_list = list(g.params.mapping_dict.values())

    for name in result_df.query("id==0").sort_values("total_point", ascending=False)["name"]:
        work_stats = StatsInfo()
        if str(name) not in g.params.player_list:
            continue
        work_stats.set_parameter(**g.params.placeholder())
        work_stats.name = str(name)
        work_stats.set_data(result_df.query("name == @name"))
        work_stats.set_data(record_df.query("name == @name"))
        work_stats.set_rank(rank_df.query("name == @name"))
        stats_df = pd.concat([stats_df, work_stats.summary])

    if stats_df.empty:
        m.set_headline(message.random_reply(m, "no_hits"), StyleOptions())
        m.status.result = False
        return

    # 規定打数足切り
    stats_df.query("count >= @g.params.stipulated", inplace=True)
    if stats_df.empty:
        m.set_headline(message.random_reply(m, "no_target"), StyleOptions())
        m.status.result = False
        return

    if g.params.anonymous:
        mapping_dict = textutil.anonymous_mapping(stats_df.index.to_list())
        stats_df.index = list(mapping_dict.values())

    # 詳細オプション指定時項目
    if not g.params.verbose:
        stats_df.drop(
            columns=[
                "avg_balance",
                "lose2_balance",
                "lose2_max",
                "lose3_max",
                "lose4_max",
                "point_max",
                "point_min",
                "rank1_balance",
                "rank2_balance",
                "rank3_balance",
                "rank4_balance",
                "rpoint_max",
                "rpoint_min",
                "top1_max",
                "top2_balance",
                "top2_max",
                "top2_rate-count",
                "top3_max",
                "top3_rate-count",
            ],
            inplace=True,
        )

    # 非表示項目
    if g.cfg.rule.get_draw_split(g.params.rule_version):
        stats_df.drop(
            columns=[
                "rank1_rate-count",
                "rank2_rate-count",
                "rank3_rate-count",
                "rank4_rate-count",
                "top2_balance",
                "lose2_balance",
                "rank1_balance",
                "rank2_balance",
                "rank3_balance",
                "rank4_balance",
            ],
            inplace=True,
        )
    stats_df.drop(columns=dictutil.dropitems_list(stats_df.columns.to_list()), inplace=True)

    # 出力
    options: StyleOptions = StyleOptions(
        title=title,
        data_kind=StyleOptions.DataKind.STATS_LIST,
        base_name="stats_list",
        show_index=True,
        codeblock=True,
        transpose=True,
    )

    match g.params.format.lower():
        case "csv":
            options.format_type = "csv"
            data = converter.save_output(stats_df, options, m.post.headline)
        case "text" | "txt":
            options.format_type = "txt"
            data = converter.save_output(stats_df, options, m.post.headline)
        case _:
            options.key_title = False
            data = stats_df.rename(columns=dictutil.rename_dicts(stats_df.columns.to_list(), options)).T

    m.set_message(data, options)
    m.post.thread = True


def rank_information(game_info: GameInfo) -> str:
    """
    順位情報（ヘッダ）メッセージを生成

    Args:
        game_info (GameInfo): _description_

    Returns:
        str: 生成メッセージ
    """
    ret: dict[str, Any] = {}

    ret["1位"] = f"{game_info.stats.seat0.rank(1):2} 回 ({game_info.stats.seat0.rank_rate(1):7.2%})"
    if game_info.stats.seat0.rank(1.5):
        ret["1.5位"] = f"{game_info.stats.seat0.rank(1.5):2} 回 ({game_info.stats.seat0.rank_rate(1.5):7.2%})"
    ret["2位"] = f"{game_info.stats.seat0.rank(2):2} 回 ({game_info.stats.seat0.rank_rate(2):7.2%})"
    if game_info.stats.seat0.rank(2.5):
        ret["2.5位"] = f"{game_info.stats.seat0.rank(2.5):2} 回 ({game_info.stats.seat0.rank_rate(2.5):7.2%})"
    ret["3位"] = f"{game_info.stats.seat0.rank(3):2} 回 ({game_info.stats.seat0.rank_rate(3):7.2%})"
    if game_info.stats.seat0.rank(3.5):
        ret["3.5位"] = f"{game_info.stats.seat0.rank(3.5):2} 回 ({game_info.stats.seat0.rank_rate(3.5):7.2%})"
    if g.params.mode == 4:
        ret["4位"] = f"{game_info.stats.seat0.rank(4):2} 回 ({game_info.stats.seat0.rank_rate(4):7.2%})"
    ret["トビ"] = f"{game_info.stats.seat0.flying:2} 回 ({game_info.stats.seat0.flying_rate:7.2%})"
    ret["役満"] = f"{game_info.stats.seat0.yakuman:2} 回 ({game_info.stats.seat0.yakuman_rate:7.2%})"

    # 非表示項目
    msg: list[str] = [f"{k}：{v}" for k, v in ret.items() if k not in dictutil.dropitems_list()]

    return "\n".join(msg).strip()


def totalization(game_info: GameInfo) -> str:
    """
    集計トータル（ヘッダ）メッセージ生成

    Args:
        game_info (GameInfo): 成績情報

    Returns:
        str: 生成メッセージ

    """
    ret: dict[str, Any] = {}

    ret["対戦数"] = "{war_record} {badge_status}".format(
        war_record=game_info.stats.seat0.war_record(),
        badge_status=badge.status(game_info.stats.seat0.count, game_info.stats.seat0.win),
    ).strip()
    ret["通算ポイント"] = f"{game_info.stats.seat0.total_point:+.1f}pt".replace("-", "▲")
    ret["平均ポイント"] = f"{game_info.stats.seat0.avg_point:+.1f}pt".replace("-", "▲")
    ret["平均順位"] = f"{game_info.stats.seat0.rank_avg:1.2f}"
    if all([g.params.individual, g.adapter.conf.badge_grade, not g.cfg.rule.get_draw_split(g.params.rule_version)]):
        ret["段位"] = badge.grade(g.params.player_name)

    # 非表示項目
    msg: list[str] = [f"{k}：{v}" for k, v in ret.items() if k not in dictutil.dropitems_list()]

    return "\n".join(msg).strip()


def results_simple() -> pd.DataFrame:
    """
    戦績(簡易)データ取得

    Returns:
        pd.DataFrame: 戦績データ

    """
    target_player = textutil.name_replace(g.params.target_player[0], add_mark=True)

    df = g.params.read_data("SUMMARY_DETAILS").fillna(value="")
    target_player = g.params.mapping_dict.get(target_player, target_player)

    df_data = df.query("name == @target_player")
    df_data["seat"] = df_data.apply(lambda v: ["東家", "南家", "西家", "北家"][(v["seat"] - 1)], axis=1)
    df_data["rpoint"] = df_data["rpoint"] * 100
    pd.options.mode.copy_on_write = True
    if g.params.individual:
        df_data.loc[:, "memo"] = np.where(df_data["guest_count"] >= 2, "2ゲスト戦", "")
    else:
        df_data.loc[:, "memo"] = np.where(df_data["same_team"] == 1, "チーム同卓", "")
    df_data = df_data.filter(items=["playtime", "seat", "rank", "rpoint", "point", "remarks", "memo"])

    return df_data


def results_details() -> pd.DataFrame:
    """
    戦績(詳細)データ取得

    Returns:
        pd.DataFrame: 戦績データ

    """
    target_player = textutil.name_replace(g.params.target_player[0], add_mark=True)
    mapping_dict = g.params.mapping_dict

    df = g.params.read_data("SUMMARY_DETAILS2").fillna(value="")
    if g.params.anonymous:
        name_list: list[str] = []
        name_list.extend(df["p1_name"].unique().tolist())
        name_list.extend(df["p2_name"].unique().tolist())
        name_list.extend(df["p3_name"].unique().tolist())
        name_list.extend(df["p4_name"].unique().tolist())
        mapping_dict.update(textutil.anonymous_mapping(list(set(name_list)), len(mapping_dict)))
        df["p1_name"] = df["p1_name"].replace(mapping_dict)
        df["p2_name"] = df["p2_name"].replace(mapping_dict)
        df["p3_name"] = df["p3_name"].replace(mapping_dict)
        df["p4_name"] = df["p4_name"].replace(mapping_dict)
        target_player = mapping_dict.get(target_player, target_player)

    match g.params.mode:
        case 3:
            df.drop(columns=["p4_name", "p4_rpoint", "p4_rank", "p4_point", "p4_remarks"], inplace=True)
            df_data = df.query(
                "p1_name == @target_player or p2_name == @target_player or p3_name == @target_player"  # noqa: E501
            )
        case 4:
            df_data = df.query(
                "p1_name == @target_player or p2_name == @target_player or p3_name == @target_player or p4_name == @target_player"  # noqa: E501
            )
        case _:
            return pd.DataFrame()

    pd.options.mode.copy_on_write = True
    if g.params.individual:
        df_data.loc[:, "memo"] = np.where(df_data["guest_count"] >= 2, "2ゲスト戦", "")
    else:
        df_data.loc[:, "memo"] = np.where(df_data["same_team"] == 1, "チーム同卓", "")
    df_data = df_data.drop(columns=["guest_count", "same_team"])

    return df_data


def df_to_seat_data(df: pd.DataFrame) -> str:
    """
    座席データ生成

    Args:
        df (pd.DataFrame): 対象データ

    Returns:
        str: 整形テキスト

    """
    df.rename(columns=dictutil.rename_dicts(df.columns.to_list()), inplace=True)

    # 表示加工
    df["席"] = df.apply(lambda x: f"{x['席']}：", axis=1)
    df["順位分布(平均順位)"] = df.apply(lambda x: f"{x['順位分布']} ({x['平均順位']})", axis=1)
    if "トビ" in df.columns:
        df["トビ"] = df.apply(lambda x: f"/ {x['トビ']:3d}", axis=1)
    if "役満和了" in df.columns:
        df["役満和了"] = df.apply(lambda x: f"/ {x['役満和了']:3d}", axis=1)

    #
    if g.cfg.rule.get_draw_split(g.params.rule_version):
        filter_items = ["席", "平均順位", "トビ", "役満和了"]
    else:
        filter_items = ["席", "順位分布(平均順位)", "トビ", "役満和了"]
    df = df.filter(items=filter_items).rename(columns={"席": "# 席：", "トビ": "/ トビ", "役満和了": "/ 役満 #"})

    #
    tbl = df.to_markdown(tablefmt="tsv", index=False).replace("0.00", "-.--").replace(" \t", "")
    return f"{tbl}\n"


def versus_data() -> str:
    """
    対戦結果データ出力用メッセージ生成

    Returns:
        str: 出力メッセージ

    """
    df = g.params.read_data("SUMMARY_versus")
    mapping_dict = g.params.mapping_dict

    if df.empty:
        return ""

    if g.params.anonymous:
        mapping_dict.update(textutil.anonymous_mapping(df["vs_name"].unique().tolist(), len(mapping_dict)))
        df["my_name"] = df["my_name"].replace(mapping_dict)
        df["vs_name"] = df["vs_name"].replace(mapping_dict)

    data_list: list[list[str]] = []
    for _, r in df.iterrows():
        data_list.append([r["vs_name"], f"{r['game']} 戦", f"{r['win']} 勝", f"{r['lose']} 敗", f"({r['win%']:6.2f}%)"])

    output = table2ascii(
        # header=["対戦相手", "対戦数", "勝", "負", "勝率"],
        body=data_list,
        alignments=[Alignment.LEFT, Alignment.RIGHT, Alignment.RIGHT, Alignment.RIGHT, Alignment.RIGHT],
        style=PresetStyle.ascii_borderless,
        cell_padding=0,
    )

    return output
