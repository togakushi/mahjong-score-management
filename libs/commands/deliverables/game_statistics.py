"""
ゲーム統計情報
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import message
from libs.types import CommandType, StyleOptions

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def plot(m: "MessageParserProtocol") -> None:
    """
    ゲーム統計表の生成

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = CommandType.GAME_STATISTICS

    # データ収集
    title: str = "月間ゲーム統計"
    if g.params.collection == "yearly":
        title = "年間ゲーム統計"

    game_info = GameInfo()
    df = g.params.read_data("REPORT_GAME_STATISTICS")

    if df.empty:
        m.set_headline(message.random_reply(m, "no_hits"), StyleOptions(title=title))
        m.status.result = False
        return

    m.set_headline(message.header(game_info, m, "", 1), StyleOptions(title=title))
    m.set_message(
        df,
        StyleOptions(
            title=title,
            key_title=False,
            data_kind=StyleOptions.DataKind.POINTS_TOTAL,
            rename_type=StyleOptions.RenameType.SHORT,
            codeblock=True,
        ),
    )
