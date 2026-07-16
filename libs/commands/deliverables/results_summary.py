"""
成績サマリ
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import message
from libs.types import CommandType, StyleOptions
from libs.utils import converter, dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.types import MessageType


def aggregation(m: "MessageParserProtocol") -> None:
    """
    各プレイヤーの通算ポイントを表示

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = CommandType.RECORD_SUMMARY

    # データ収集
    data: "MessageType"
    game_info = GameInfo()
    df_summary = g.params.read_data("SUMMARY_TOTAL")
    df_remarks = g.params.read_data("REMARKS_INFO")

    # 順位分布選択
    match g.params.mode:
        case 3:
            df_summary.drop(columns=["rank_distr4"], inplace=True)
        case 4:
            df_summary.drop(columns=["rank_distr3"], inplace=True)

    # インデックスの振りなおし
    df_summary.reset_index(inplace=True, drop=True)
    df_summary.index += 1

    # 情報ヘッダ
    current_rule: str = ""
    for rule in g.params.rule_list:
        current_rule = rule

    if g.params.individual:  # 個人集計
        headline_title = "成績サマリ"
    else:  # チーム集計
        headline_title = "チーム成績サマリ"

    add_text = "" if g.cfg.rule.get_ignore_flying(current_rule) else f"/ トバされた人（延べ）：{df_summary['flying'].sum()} 人"
    m.set_headline(message.header(game_info, m, add_text, 1), StyleOptions(title=headline_title))

    if df_summary.empty:
        m.status.result = False
        return

    # 共通オプション
    options = StyleOptions(
        key_title=True,
        rename_type=StyleOptions.RenameType.SHORT,
        data_kind=StyleOptions.DataKind.POINTS_TOTAL,
    )
    match g.params.format.lower():
        case "csv":
            options.format_type = "csv"
        case "txt" | "text":
            options.format_type = "txt"
        case _:
            options.format_type = "default"

    if g.cfg.rule.get_draw_split(g.params.rule_version):
        header_list = ["name", "total_point", "avg_point", "rank_avg", "flying"]
        filter_list = ["name", "count", "total_point", "avg_point", "diff_from_above", "diff_from_top", "rank_avg", "flying"]
    else:
        header_list = ["name", "total_point", "avg_point", "rank_distr3", "rank_distr4", "flying"]
        filter_list = [
            "name",
            "count",
            "total_point",
            "avg_point",
            "diff_from_above",
            "diff_from_top",
            "rank1",
            "rank2",
            "rank3",
            "rank4",
            "rank_avg",
            "flying",
        ]

    # 非表示項目
    df_summary.drop(columns=dictutil.dropitems_list(df_summary.columns.to_list()), inplace=True)
    df_remarks.drop(columns=dictutil.dropitems_list(df_remarks.columns.to_list()), inplace=True)

    # 通算ポイント
    if options.format_type == "default":
        options.title = "通算ポイント"
        options.codeblock = True
        data = df_summary.filter(items=header_list)
    else:
        options.title = f"{headline_title}：通算ポイント"
        options.base_name = "summary"
        df_summary = df_summary.filter(items=filter_list).fillna("*****")
        data = converter.save_output(df_summary, options, m.post.headline, "summary")
    m.set_message(data, StyleOptions(**options.asdict))

    # メモ(役満和了)
    if "役満和了" not in dictutil.dropitems_list():
        options.data_kind = StyleOptions.DataKind.REMARKS_YAKUMAN
        df_yakuman = df_remarks.query("type == 0").drop(columns=["type", "ex_point"])

        if options.format_type == "default":
            options.title = "役満和了"
            options.codeblock = False
            data = df_yakuman
        else:
            options.title = f"{headline_title}：役満和了"
            options.base_name = "yakuman"
            data = converter.save_output(df_yakuman, options, m.post.headline, "yakuman")
        m.set_message(data, StyleOptions(**options.asdict))

    # メモ(卓外清算)
    if "卓外清算" not in dictutil.dropitems_list():
        options.data_kind = StyleOptions.DataKind.REMARKS_REGULATION

        if g.params.individual:  # 個人集計
            df_regulations = df_remarks.query("type == 2").drop(columns=["type"])
        else:  # チーム集計
            df_regulations = df_remarks.query("type == 2 or type == 3").drop(columns=["type"])

        if options.format_type == "default":
            options.title = "卓外清算"
            options.codeblock = False
            data = df_regulations
        else:
            options.title = f"{headline_title}：卓外清算"
            options.base_name = "regulations"
            data = converter.save_output(df_regulations, options, m.post.headline, "regulations")
        m.set_message(data, StyleOptions(**options.asdict))

    # メモ(その他)
    if "その他" not in dictutil.dropitems_list():
        options.data_kind = StyleOptions.DataKind.REMARKS_OTHER
        df_others = df_remarks.query("type == 1").drop(columns=set(df_remarks.columns) & {"type", "ex_point"})

        if options.format_type == "default":
            options.title = "その他"
            options.codeblock = False
            data = df_others
        else:
            options.title = f"{headline_title}：その他"
            options.base_name = "others"
            data = converter.save_output(df_others, options, m.post.headline, "others")
        m.set_message(data, StyleOptions(**options.asdict))


def difference(m: "MessageParserProtocol") -> None:
    """
    各プレイヤーのポイント差分を表示

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = CommandType.RECORD_SUMMARY

    # データ収集
    data: "MessageType"
    game_info = GameInfo()
    df_summary = g.params.read_data("SUMMARY_TOTAL")

    # 順位分布選択
    match g.params.mode:
        case 3:
            df_summary.drop(columns=["rank_distr4"], inplace=True)
        case 4:
            df_summary.drop(columns=["rank_distr3"], inplace=True)

    # インデックスの振りなおし
    df_summary.reset_index(inplace=True, drop=True)
    df_summary.index += 1

    # 情報ヘッダ
    current_rule: str = ""
    for rule in g.params.rule_list:
        current_rule = rule

    if g.params.individual:  # 個人集計
        headline_title = "成績サマリ"
    else:  # チーム集計
        headline_title = "チーム成績サマリ"

    add_text = "" if g.cfg.rule.get_ignore_flying(current_rule) else f"/ トバされた人（延べ）：{df_summary['flying'].sum()} 人"
    m.set_headline(message.header(game_info, m, add_text, 1), StyleOptions(title=headline_title))

    if df_summary.empty:
        m.status.result = False
        return

    options = StyleOptions(
        title="通算ポイント(差分)",
        base_name="summary",
        codeblock=True,
        summarize=True,
        rename_type=StyleOptions.RenameType.SHORT,
        data_kind=StyleOptions.DataKind.POINTS_DIFF,
    )
    match g.params.format.lower():
        case "csv":
            options.format_type = "csv"
        case "txt" | "text":
            options.format_type = "txt"
        case _:
            options.format_type = "default"

    # 集計結果
    header_list = ["#", "name", "total_point", "rank_avg", "diff_from_above", "diff_from_top"]
    filter_list = ["name", "count", "total_point", "rank_avg", "diff_from_above", "diff_from_top"]

    # 非表示項目
    df_summary.drop(columns=dictutil.dropitems_list(df_summary.columns.to_list()), inplace=True)

    if options.format_type == "default":
        data = df_summary.filter(items=header_list)
    else:
        options.title = headline_title
        data = converter.save_output(df_summary.filter(items=filter_list).fillna("*****"), options, m.post.headline)

    m.set_message(data, StyleOptions(**options.asdict))
