"""
libs/commands/ranking/rating.py
"""

from typing import TYPE_CHECKING

import pandas as pd

import libs.global_value as g
from libs.domain import aggregate
from libs.domain.datamodels import GameInfo
from libs.functions import message
from libs.functions.compose import badge
from libs.types import CommandType, StyleOptions
from libs.utils import converter, formatter

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.types import MessageType


def aggregation(m: "MessageParserProtocol") -> None:
    """
    レーティングを集計して返す

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    m.status.command_type = CommandType.RATING  # 更新

    # 情報ヘッダ
    title: str = "レーティング"
    add_text: str = ""

    if g.params.mode == 3 or g.params.target_mode == 3:  # todo: 未実装
        m.set_headline(message.random_reply(m, "not_implemented"), StyleOptions(title=title))
        m.status.result = False
        return

    # データ収集
    game_info = GameInfo()

    if not game_info.count:  # 検索結果が0件のとき
        m.set_headline(message.random_reply(m, "no_hits"), StyleOptions())
        m.status.result = False
        return

    df_results = g.params.read_data("RANKING_RESULTS").set_index("name")
    df_ratings = aggregate.calculation_rating()

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
    if g.adapter.conf.badge_grade:
        for idx in df.index:
            name = str(df.at[idx, "name"]).replace(f"({g.cfg.setting.guest_mark})", "")
            df.at[idx, "grade"] = badge.grade(name, False)

    # 表示
    if g.params.anonymous:
        mapping_dict = formatter.anonymous_mapping(df["name"].unique().tolist())
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

    # 非表示項目を削除
    df = formatter.df_drop(df, list(g.cfg.rule.dropitems(g.params.rule_version)))

    m.set_headline(message.header(game_info, m, add_text, 1), StyleOptions(title=title))
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
