"""
libs/domain/aggregate.py
"""

from typing import Optional

import numpy as np
import pandas as pd

import libs.global_value as g


def game_summary(
    filter_items: Optional[list[str]] = None,
    drop_items: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    ゲーム結果をサマライズする

    Args:
        filter_items (Optional[list[str]]): 抽出するカラム. Defaults to None.
        drop_items (Optional[list[str]]): 除外するカラム. Defaults to None.

    Returns:
        pd.DataFrame: 集計結果

    """
    # データ収集
    df = g.params.read_data("SUMMARY_TOTAL")

    # 順位分布選択
    match g.params.mode:
        case 3:
            df = df.drop(columns=["rank_distr4"])
        case 4:
            df = df.drop(columns=["rank_distr3"])

    if isinstance(filter_items, list):
        df = df.filter(items=filter_items)

    if isinstance(drop_items, list):
        df = df.drop(columns=drop_items)

    return df


def calculation_rating() -> pd.DataFrame:
    """
    レーティング集計

    Returns:
        pd.DataFrame: 集計結果

    """
    # データ収集
    df_results = g.params.read_data("RANKING_RATINGS").set_index("playtime")
    df_ratings = pd.DataFrame(index=["initial_rating"] + df_results.index.to_list())  # 記録用
    last_ratings: dict[str, float] = {}  # 最終値格納用

    # 獲得スコア
    score_mapping = {"1.0": 30.0, "1.5": 20.0, "2.0": 10.0, "2.5": 0.0, "3.0": -10.0, "3.5": -20.0, "4.0": -30.0}

    for x in df_results.itertuples():
        player_list = (str(x.p1_name), str(x.p2_name), str(x.p3_name), str(x.p4_name))
        for player in player_list:
            if player not in df_ratings.columns:
                last_ratings[player] = 1500.0
                df_ratings[player] = np.nan
                df_ratings.loc["initial_rating", player] = 1500.0
                df_ratings = df_ratings

        # 天鳳計算式 (https://tenhou.net/man/#RATING)
        rank_list = (x.p1_rank, x.p2_rank, x.p3_rank, x.p4_rank)
        rating_list = [last_ratings[player] for player in player_list]
        rating_avg = float(1500.0 if np.mean(rating_list) < 1500.0 else np.mean(rating_list))

        for i, player in enumerate(player_list):
            rating = float(rating_list[i])
            rank = "{:.1f}".format(float(str(rank_list[i])))

            correction_value: float = (rating_avg - rating) / 40
            if df_ratings[player].count() >= 400:
                match_correction = 0.2
            else:
                match_correction = 1 - df_ratings[player].count() * 0.002

            new_rating = rating + match_correction * (score_mapping.get(rank, 0.0) + correction_value)

            last_ratings[player] = new_rating
            df_ratings.loc[x.Index, player] = new_rating

    # 間引き(集約オプション)
    if collection := g.params.collection:
        ratings = df_ratings[1:]
        ratings.index = pd.to_datetime(ratings.index)  # DatetimeIndexに変換

        match collection:
            case "daily":
                ratings = ratings.resample("D").last().ffill()
            case "monthly":
                ratings = ratings.resample("ME").last().ffill()
            case "yearly":
                ratings = ratings.resample("YE").last().ffill()
            case "all":
                ratings = df_ratings.ffill().tail(1)
            case _:
                return df_ratings

        ratings.index = ratings.index.astype(str)
        df_ratings = pd.concat([df_ratings.head(1), ratings])

    return df_ratings
