"""
レーティング
"""

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import message
from libs.functions.compose import badge
from libs.types import StyleOptions
from libs.utils import converter, dictutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.types import MessageType


def aggregation(m: "MessageParserProtocol") -> None:
    """
    レーティングを集計して返す

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.RATING

    # ヘッダ情報
    title: str = "レーティング"
    add_text: str = ""

    if g.params.mode == 3 or g.params.target_mode == 3:  # todo: 未実装
        m.set_headline(message.random_reply(m, "not_implemented"), StyleOptions(title=title))
        m.status.result = False
        return

    # データ収集
    game_info = GameInfo()
    m.set_headline(message.header(game_info, m, add_text, 1), StyleOptions(title=title))

    if not game_info.count:  # 検索結果が0件のとき
        m.status.result = False
        return

    df_results = g.params.read_data("RANKING_RESULTS", False).set_index("name")
    df_ratings = calculation_rating()

    # 最終的なレーティング
    final = df_ratings.ffill().tail(1).transpose()
    final.columns = ["rate"]
    final["name"] = final.index

    df = pd.merge(df_results, final, on=["name"]).sort_values(by="rate", ascending=False)
    df = df.query("count >= @g.params.stipulated")  # 足切り
    df["rank"] = 0  # 順位表示用カラム

    # 集計対象外データの削除
    if g.params.unregistered_replace:  # 個人戦
        for player in df.itertuples():
            if player.name not in g.cfg.member.lists:
                df = df.drop(player.Index)

    if not g.params.individual:  # チーム戦
        df = df.query("name != '未所属'")

    # 順位偏差 / 得点偏差
    df["point_dev"] = round((df["rpoint_avg"] - df["rpoint_avg"].mean()) / df["rpoint_avg"].std(ddof=0) * 10 + 50, 1)
    df["rank_dev"] = round((df["rank_avg"] - df["rank_avg"].mean()) / df["rank_avg"].std(ddof=0) * -10 + 50, 1)

    # 段位
    if g.adapter.conf.badge_grade and not g.cfg.rule.get_draw_split(g.params.rule_version):
        for idx in df.index:
            name = str(df.at[idx, "name"]).replace(f"({g.cfg.setting.guest_mark})", "")
            df.at[idx, "grade"] = badge.grade(name, False)

    # 表示
    if g.params.anonymous:
        mapping_dict = textutil.anonymous_mapping(df["name"].unique().tolist())
        df["name"] = df["name"].replace(mapping_dict)

    if df.empty:
        m.set_headline(message.random_reply(m, "no_target"), StyleOptions())
        m.status.result = False
        return

    df["rank"] = df["rate"].rank(ascending=False, method="dense").astype("int")
    df["rate"] = df["rate"].map(lambda v: round(v, 1))
    df = df.query("rank <= @g.params.ranked").filter(
        items=["rank", "name", "rate", "rank_distr", "rank_avg", "rank_dev", "rpoint_avg", "point_dev", "grade"],
    )

    # 非表示項目
    df.drop(columns=dictutil.dropitems_list(df.columns.to_list()), inplace=True)

    options: StyleOptions = StyleOptions(
        title=title,
        data_kind=StyleOptions.DataKind.RATING,
        rename_type=StyleOptions.RenameType.SHORT,
        base_name="rating",
        format_type="default",
        summarize=False,
        codeblock=True,
    )

    data: "MessageType"
    match g.params.format.lower():
        case "csv":
            options.format_type = "csv"
            data = converter.save_output(df, options, m.post.headline)
        case "text" | "txt":
            options.format_type = "txt"
            data = converter.save_output(df, options, m.post.headline)
        case _:
            options.key_title = False
            data = df

    m.set_message(data, options)


def calculation_rating() -> pd.DataFrame:
    """
    レーティング集計

    Returns:
        pd.DataFrame: 集計結果

    """
    # データ収集
    df_results = g.params.read_data("RANKING_RATINGS", False).set_index("playtime")
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
