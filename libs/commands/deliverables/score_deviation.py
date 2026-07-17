"""
素点分析
"""

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import adjusting, message
from libs.types import StyleOptions
from libs.utils import converter, dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.types import MessageType


def aggregation(m: "MessageParserProtocol") -> None:
    """
    各プレイヤーの素点情報の偏りを表示

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.ANALYSIS_SCORES

    # データ収集
    data: "MessageType"
    rank_data: dict[str, list[float]] = {}
    game_info = GameInfo()
    total_df = g.params.read_data("SUMMARY_DETAILS")

    rank1_avg = total_df.query("rank == 1")["rpoint"].mean(skipna=False)
    rank2_avg = total_df.query("rank == 2")["rpoint"].mean(skipna=False)
    rank3_avg = total_df.query("rank == 3")["rpoint"].mean(skipna=False)
    rank4_avg = total_df.query("rank == 4")["rpoint"].mean(skipna=False)

    for player_name in total_df["name"].unique():
        work_df = total_df.query("name == @player_name")
        player_count = len(work_df)
        player_rank_avg = work_df["rpoint"].mean(skipna=False)
        player_rank1_avg = np.nan
        player_rank2_avg = np.nan
        player_rank3_avg = np.nan
        player_rank4_avg = np.nan

        if not work_df.query("rank == 1").empty:
            player_rank1_avg = work_df.query("rank == 1")["rpoint"].mean(skipna=False)
        if not work_df.query("rank == 2").empty:
            player_rank2_avg = work_df.query("rank == 2")["rpoint"].mean(skipna=False)
        if not work_df.query("rank == 3").empty:
            player_rank3_avg = work_df.query("rank == 3")["rpoint"].mean(skipna=False)
        if not work_df.query("rank == 4").empty:
            player_rank4_avg = work_df.query("rank == 4")["rpoint"].mean(skipna=False)

        rank_data.update(
            {
                player_name: [
                    player_count,
                    round(float(work_df["rank"].mean(skipna=False)), 2),
                    round(float(player_rank_avg * 100), 1),
                    round(float((player_rank1_avg - rank1_avg) * 100), 1),
                    round(float((player_rank2_avg - rank2_avg) * 100), 1),
                    round(float((player_rank3_avg - rank3_avg) * 100), 1),
                    round(float((player_rank4_avg - rank4_avg) * 100), 1),
                ],
            }
        )

    #
    index_label = ["count", "rank_avg", "rpoint_avg", "rank1_avg_diff", "rank2_avg_diff", "rank3_avg_diff", "rank4_avg_diff"]
    rank_df = pd.DataFrame.from_dict(rank_data, orient="index", columns=index_label).rename_axis("name")
    rank_df.sort_values("rank_avg", ascending=True, inplace=True)

    # 足切り
    rank_df = rank_df.query("count >= @g.params.stipulated")

    # 情報ヘッダ
    headline_title = "素点分析"
    header_text = message.header(game_info, m, "", 1)
    m.set_headline(header_text, StyleOptions(title=headline_title))

    # 非表示項目
    rank_df.drop(columns=dictutil.dropitems_list(rank_df.columns.to_list()), inplace=True)

    options = StyleOptions(
        title=headline_title,
        base_name="score_deviation",
        show_index=True,
        codeblock=False,
        key_title=False,
        rename_type=StyleOptions.RenameType.SHORT,
        data_kind=StyleOptions.DataKind.SCORE_ANALYSIS,
    )

    match g.params.format.lower():
        case "csv":
            options.format_type = "csv"
            data = converter.save_output(rank_df.fillna("*****"), options, m.post.headline)
        case "txt" | "text":
            options.format_type = "txt"
            rank_df = adjusting.add_units(rank_df.fillna("*****"))
            data = converter.save_output(rank_df, options, m.post.headline)
        case _:
            options.format_type = "default"
            options.codeblock = True
            data = rank_df

    m.set_message(data, StyleOptions(**options.asdict))
