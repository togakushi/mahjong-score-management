"""
ゲーム統計情報
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import adjusting, message
from libs.types import MessageType, StyleOptions
from libs.utils import converter

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def plot(m: "MessageParserProtocol") -> None:
    """
    ゲーム統計表の生成

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.GAME_STATISTICS

    # ヘッダ情報
    title: str = "月間ゲーム統計"
    if g.params.collection == "yearly":
        title = "年間ゲーム統計"

    # データ収集
    game_info = GameInfo()
    df = g.params.read_data("REPORT_GAME_STATISTICS")
    m.set_headline(message.header(game_info, m, "", 1), StyleOptions(title=title))

    if df.empty:
        m.status.result = False
        return

    # 出力内容
    data: MessageType
    options = StyleOptions(
        title=title,
        key_title=False,
        data_kind=StyleOptions.DataKind.GAME_STATISTICS,
        rename_type=StyleOptions.RenameType.SHORT,
        codeblock=True,
        summarize=False,
        base_name=str(m.status.command_type),
    )

    match g.params.format.lower():
        case "csv":
            options.format_type = "csv"
            data = converter.save_output(df, options, m.post.headline)
        case "txt" | "text":
            options.format_type = "txt"
            data = converter.save_output(df, options, m.post.headline)
        case _:
            options.format_type = "default"
            data = adjusting.add_units(df)

    m.set_message(data, options)
