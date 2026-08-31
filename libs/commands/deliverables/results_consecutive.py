"""
連続戦集計
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import adjusting, message
from libs.types import StyleOptions
from libs.utils import converter

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.types import MessageType


def aggregation(m: "MessageParserProtocol") -> None:
    """
    連続戦の結果を集計

    Args:
        m (MessageParserProtocol): メッセージデータ
    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.GAME_RESULTS
    if g.params.chain == 1:
        if g.params.reverse:
            headline_title = "最低獲得ポイント"
        else:
            headline_title = "最高獲得ポイント"
    else:
        headline_title = "連続戦成績"

    # データ収集
    data: "MessageType"
    game_info = GameInfo()
    m.set_headline(message.header(game_info, m), StyleOptions(title=headline_title))
    if not g.params.chain:
        m.set_message(message.random_reply(m, "no_target"), StyleOptions(title=headline_title, key_title=False))
        m.status.result = False
        return

    df = g.params.read_data("SUMMARY_CONSECUTIVE")

    # 表示調整
    items: list[str] = ["name", "rolling_point", "acquisition_rank"]
    if g.params.verbose:
        items.extend(["start_time", "end_time", "total_game"])
    if g.params.game_results:
        if g.params.ignore_flying:
            items.extend(["consecutive_record", "total_game"])
        else:
            items.extend(["consecutive_record", "flying_count", "total_game"])
    if g.params.chain == 1:
        items.append("start_time")
        if "consecutive_record" in items:
            items.remove("consecutive_record")
        if "end_time" in items:
            items.remove("end_time")

    # 結果保存
    options = StyleOptions(
        title=headline_title,
        codeblock=True,
        key_title=False,
        format_type=g.params.format,
        base_name="summary",
        rename_type=StyleOptions.RenameType.SHORT,
        data_kind=StyleOptions.DataKind.POINTS_CONSECUTIVE,
    )
    match g.params.format:
        case "csv":
            data = converter.save_output(df, options, m.post.headline, "summary")
        case "txt":
            data = converter.save_output(
                adjusting.add_units(df.drop(columns=list(set(df.columns) - set(items)))),
                options,
                m.post.headline,
                "summary",
            )
        case _:
            data = df.drop(columns=list(set(df.columns) - set(items)))
    m.set_message(data, StyleOptions(**options.asdict))
