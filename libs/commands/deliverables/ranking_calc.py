"""
ランキング
"""

from typing import TYPE_CHECKING

import pandas as pd

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import message
from libs.types import CommandType, StyleOptions
from libs.utils import dictutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def aggregation(m: "MessageParserProtocol") -> None:
    """
    ランキングデータを生成

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = CommandType.RANKING

    # ヘッダ情報
    if g.params.individual:  # 個人集計
        title = "ランキング"
    else:  # チーム集計
        title = "チームランキング"

    # データ取得
    game_info = GameInfo()
    m.set_headline(message.header(game_info, m, "", 1), StyleOptions(title=title))

    if not game_info.count:  # 検索結果が0件のとき
        m.status.result = False
        return

    df = (
        pd.concat(
            [
                g.params.read_data("RESULTS_INFO").query("id==0").drop(columns=["id", "seat"]),
                g.params.read_data("RECORD_INFO").query("id==0").drop(columns=["id", "seat", "name"]),
            ],
            axis=1,
        )
        .drop(columns=["first_game", "last_game", "first_comment", "last_comment"])
        .query("count>=@g.params.stipulated")
    )

    if df.empty:
        m.set_headline(message.random_reply(m, "no_target"), StyleOptions())
        m.status.result = False
        return

    df["participation_rate"] = df["count"] / game_info.count  # ゲーム参加率
    df["avg_balance"] = df["score"] * 100 / df["count"]  # 平均収支
    df["rank1_rate"] = df["rank1"] / df["count"]  # トップ率
    df["top2_rate"] = (df["rank1"] + df["rank2"]) / df["count"]  # 連対率
    df["top3_rate"] = (df["rank1"] + df["rank2"] + df["rank3"]) / df["count"]  # ラス回避率
    df["flying_rate"] = df["flying"] / df["count"]  # トビ率
    df["yakuman_rate"] = df["yakuman"] / df["count"]  # 役満和了率
    if g.params.mode == 3:
        df["rank_distr"] = [f"{x.rank1}-{x.rank2}-{x.rank3}" for x in df.itertuples()]
    else:
        df["rank_distr"] = [f"{x.rank1}-{x.rank2}-{x.rank3}-{x.rank4}" for x in df.itertuples()]

    if g.params.anonymous:
        mapping_dict = textutil.anonymous_mapping(df["name"].unique().tolist())
        df["name"] = df["name"].replace(mapping_dict)

    # 集計
    data: dict[str, pd.DataFrame] = {}

    data["ゲーム参加率"] = (
        pd.DataFrame(
            {
                "rank": df["participation_rate"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "participation_rate": df["participation_rate"] * 100,
                "count": df["count"],
                "total_count": game_info.count,
            }
        )
        .sort_values("rank")
        .query("rank <= @g.params.ranked")
    )
    data["通算ポイント"] = (
        pd.DataFrame(
            {
                "rank": df["total_point"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "total_point": df["total_point"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked")
    )
    data["平均ポイント"] = (
        pd.DataFrame(
            {
                "rank": df["avg_point"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "avg_point": df["avg_point"],
                "total_point": df["total_point"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked")
    )
    data["平均収支"] = (
        pd.DataFrame(
            {
                "rank": df["avg_balance"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "avg_balance": df["avg_balance"],
                "rpoint_avg": df["rpoint_avg"] * 100,
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked")
    )
    data["トップ率"] = (
        pd.DataFrame(
            {
                "rank": df["rank1_rate"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "rank1_rate": df["rank1_rate"] * 100,
                "rank1": df["rank1"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked")
    )
    if g.params.mode == 3:
        data["ラス回避率"] = (
            pd.DataFrame(
                {
                    "rank": df["top2_rate"].rank(ascending=False, method="dense").astype("int"),
                    "name": df["name"],
                    "top2_rate": df["top2_rate"] * 100,
                    "top2": df["rank1"] + df["rank2"],
                    "count": df["count"],
                }
            )
            .sort_values(by=["rank", "count"], ascending=[True, False])
            .query("rank <= @g.params.ranked")
        )
    else:
        data["連対率"] = (
            pd.DataFrame(
                {
                    "rank": df["top2_rate"].rank(ascending=False, method="dense").astype("int"),
                    "name": df["name"],
                    "top2_rate": df["top2_rate"] * 100,
                    "top2": df["rank1"] + df["rank2"],
                    "count": df["count"],
                }
            )
            .sort_values(by=["rank", "count"], ascending=[True, False])
            .query("rank <= @g.params.ranked")
        )
        data["ラス回避率"] = (
            pd.DataFrame(
                {
                    "rank": df["top3_rate"].rank(ascending=False, method="dense").astype("int"),
                    "name": df["name"],
                    "top3_rate": df["top3_rate"] * 100,
                    "top3": df["rank1"] + df["rank2"] + df["rank3"],
                    "count": df["count"],
                }
            )
            .sort_values(by=["rank", "count"], ascending=[True, False])
            .query("rank <= @g.params.ranked")
        )
    data["トビ率"] = (
        pd.DataFrame(
            {
                "rank": df["flying_rate"].rank(ascending=True, method="dense").astype("int"),
                "name": df["name"],
                "flying_rate": df["flying_rate"] * 100,
                "flying": df["flying"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked")
    )
    data["平均順位"] = (
        pd.DataFrame(
            {
                "rank": df["rank_avg"].rank(ascending=True, method="dense").astype("int"),
                "name": df["name"],
                "rank_avg": [f"{x.rank_avg:.2f}" for x in df.itertuples()],
                "rank_distr": df["rank_distr"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked")
    )
    data["役満和了率"] = (
        pd.DataFrame(
            {
                "rank": df["yakuman_rate"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "yakuman_rate": df["yakuman_rate"] * 100,
                "yakuman": df["yakuman"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked and yakuman > 0")
    )
    data["最大素点"] = (
        pd.DataFrame(
            {
                "rank": df["rpoint_max"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "rpoint_max": df["rpoint_max"] * 100,
                "point_max": df["point_max"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked")
    )
    data["連続トップ"] = (
        pd.DataFrame(
            {
                "rank": df["top1_max"].rank(ascending=False, method="dense").astype("int"),
                "name": df["name"],
                "top1_max": df["top1_max"],
                "count": df["count"],
            }
        )
        .sort_values(by=["rank", "count"], ascending=[True, False])
        .query("rank <= @g.params.ranked and top1_max > 1")
    )
    if g.params.mode == 3:
        data["連続ラス回避"] = (
            pd.DataFrame(
                {
                    "rank": df["top2_max"].rank(ascending=False, method="dense").astype("int"),
                    "name": df["name"],
                    "top2_max": df["top2_max"],
                    "count": df["count"],
                }
            )
            .sort_values(by=["rank", "count"], ascending=[True, False])
            .query("rank <= @g.params.ranked and top2_max > 1")
        )
    else:
        data["連続連対"] = (
            pd.DataFrame(
                {
                    "rank": df["top2_max"].rank(ascending=False, method="dense").astype("int"),
                    "name": df["name"],
                    "top2_max": df["top2_max"],
                    "count": df["count"],
                }
            )
            .sort_values(by=["rank", "count"], ascending=[True, False])
            .query("rank <= @g.params.ranked and top2_max > 1")
        )
        data["連続ラス回避"] = (
            pd.DataFrame(
                {
                    "rank": df["top3_max"].rank(ascending=False, method="dense").astype("int"),
                    "name": df["name"],
                    "top3_max": df["top3_max"],
                    "count": df["count"],
                }
            )
            .sort_values(by=["rank", "count"], ascending=[True, False])
            .query("rank <= @g.params.ranked and top3_max > 1")
        )

    # 項目整理
    dropitems = dictutil.dropitems_list(df.columns.to_list()) + dictutil.dropitems_list()
    overall_ranking: list[pd.DataFrame] = []
    for msg, df_data in data.items():
        if msg in dropitems:  # 非表示項目
            continue
        if df_data.empty:  # 対象者なし
            continue
        m.set_message(
            df_data,
            StyleOptions(
                title=msg,
                data_kind=StyleOptions.DataKind.RANKING,
                rename_type=StyleOptions.RenameType.SHORT,
                codeblock=True,
                show_index=False,
            ),
        )
        # 総合ランキング用
        if msg not in ["役満和了率"]:
            overall_ranking.append(df_data)

    # 総合ランキング
    work_df = pd.concat([df.set_index("name")["rank"] for df in overall_ranking], axis=1)
    work_df = work_df.fillna(len(work_df) + 1)
    work_df["evaluation"] = work_df.sum(axis=1).astype("int")

    overall_df = (
        pd.DataFrame(
            {
                "rank": work_df["evaluation"].rank(ascending=True, method="dense").astype("int"),
                "evaluation": work_df["evaluation"],
            }
        )
        .sort_values(["rank", "evaluation"])
        .query("rank <= @g.params.ranked")
        .reset_index()
    )
    m.set_message(
        overall_df[["rank", "name", "evaluation"]],
        StyleOptions(
            title="総合ランキング",
            data_kind=StyleOptions.DataKind.RANKING,
            rename_type=StyleOptions.RenameType.SHORT,
            codeblock=True,
            show_index=False,
        ),
    )
