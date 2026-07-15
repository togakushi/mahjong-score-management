"""
直接対戦マトリクス
"""

from typing import TYPE_CHECKING, Any

import pandas as pd

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import message
from libs.types import CommandType, StyleOptions
from libs.utils import textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def plot(m: "MessageParserProtocol") -> None:
    """
    対局対戦マトリクスの表示

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = CommandType.MATRIX

    # データ集計
    title: str = "対局対戦マトリクス"
    game_info = GameInfo()
    df = matrix_table()

    if df.empty:
        m.set_headline(message.random_reply(m, "no_target"), StyleOptions(title=title))
        m.status.result = False
        return

    if g.params.format.lower() == "csv":
        file_path = textutil.save_file_path("matrix.csv", True)
        df.to_csv(file_path)
    else:
        file_path = textutil.save_file_path("matrix.txt", True)
        df.to_markdown(file_path, tablefmt="outline")

    m.set_headline(message.header(game_info, m, "", 1), StyleOptions(title=title))
    match g.adapter.interface_type:
        case "slack" | "discord":
            m.set_message(file_path, StyleOptions(title=title, use_comment=True, header_hidden=True))
        case "web":
            m.set_message(df, StyleOptions(title=title, show_index=True))
        case _:
            m.set_message(df, StyleOptions(title=title, show_index=True))


def matrix_table() -> pd.DataFrame:
    """
    対局対戦マトリクス表の作成

    Returns:
        pd.DataFrame: 集計結果

    """
    # データ収集
    df = g.params.read_data("REPORT_MATRIX_TABLE", False).set_index("playtime")

    # 結果に含まれるプレイヤーのリスト
    plist = sorted(list(set(df["p1_name"].tolist() + df["p2_name"].tolist() + df["p3_name"].tolist() + df["p4_name"].tolist())))

    # 順位テーブルの作成
    l_data: dict[str, Any] = {}
    for pname in plist:
        if g.params.individual:  # 個人集計
            l_name = textutil.name_replace(pname)
            # プレイヤー指定があるなら対象以外をスキップ
            if g.params.player_list:
                if l_name not in g.params.player_list:
                    continue
            # ゲスト置換
            if g.params.guest_skip:  # ゲストあり
                l_name = textutil.name_replace(pname, add_mark=True)
            else:  # ゲストなし
                if pname == g.cfg.member.guest_name:
                    continue
        else:  # チーム集計
            l_name = pname

        l_data[l_name] = []
        for x in df.itertuples():
            match pname:
                case x.p1_name:
                    l_data[l_name] += [x.p1_rank]
                case x.p2_name:
                    l_data[l_name] += [x.p2_rank]
                case x.p3_name:
                    l_data[l_name] += [x.p3_rank]
                case x.p4_name:
                    l_data[l_name] += [x.p4_rank]
                case _:
                    l_data[l_name] += [None]

    # 規定打数以下を足切り
    if g.params.stipulated:
        for pname in list(l_data.keys()):
            if sum(x is not None for x in l_data[pname]) < g.params.stipulated:
                l_data.pop(pname)

    rank_df = pd.DataFrame(l_data.values(), columns=list(df.index), index=list(l_data.keys()))

    # 対象リストが0件になった場合は空のデータフレームを返す
    if rank_df.empty:
        return rank_df

    # 対局対戦マトリクス表の作成
    mtx_df = pd.DataFrame(index=list(l_data.keys()), columns=list(l_data.keys()) + ["total"])
    sorting_df = pd.DataFrame(index=list(l_data.keys()), columns=["win_per", "count"])

    for idx1 in range(len(rank_df)):
        p1 = rank_df.iloc[idx1]
        t_game_count = 0
        t_win = 0
        for idx2 in range(len(rank_df)):
            p2 = rank_df.iloc[idx2]
            if p1.name == p2.name:
                mtx_df.loc[f"{p1.name}", f"{p2.name}"] = "---"
            else:
                game_count = len(pd.concat([p1, p2], axis=1).dropna())
                win = (p1 < p2).sum()
                t_game_count += game_count
                t_win += win

                if game_count:
                    winning_per = str(round(float(win / game_count * 100), 1))
                else:
                    winning_per = "--.-"
                mtx_df.loc[f"{p1.name}", f"{p2.name}"] = f"{win}-{game_count - win} ({winning_per}%)"

        if t_game_count:
            t_winning_per = str(round(float(t_win / t_game_count * 100), 1))
        else:
            t_winning_per = "--.-"
        mtx_df.loc[f"{p1.name}", "total"] = f"{t_win}-{t_game_count - t_win} ({t_winning_per}%)"
        sorting_df.loc[f"{p1.name}", "win_per"] = t_winning_per
        sorting_df.loc[f"{p1.name}", "count"] = t_game_count

    # 勝率で並び替え
    sorting_df["win_per"] = pd.to_numeric(sorting_df["win_per"], errors="coerce")
    sorting_df["count"] = pd.to_numeric(sorting_df["count"], errors="coerce")
    sorting_df = sorting_df.sort_values(by=["win_per", "count"], ascending=[False, False])
    mtx_df = mtx_df.reindex(index=list(sorting_df.index), columns=list(sorting_df.index) + ["total"])

    if g.params.anonymous:
        mapping_dict = textutil.anonymous_mapping(mtx_df.index.tolist())
        mtx_df = mtx_df.rename(columns=mapping_dict, index=mapping_dict)

    return mtx_df
