"""
libs/commands/graph/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.bootstrap.section import SubCommands
from libs.commands.graph import personal, rating, summary
from libs.domain.datamodels import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class GraphConfig(SubCommands):
    """graphセクション処理"""

    def __init__(self) -> None:
        self.default_commandword: str = "麻雀グラフ"
        self.section: str = str(CommandType.GRAPH)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    グラフ生成処理エントリーポイント

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    m.status.command_type = CommandType.GRAPH
    g.params = dictutil.placeholder(g.cfg.graph, m)

    if len(g.params.player_list) == 1:  # 対象がひとり
        if g.params.statistics:
            personal.statistics_plot(m)
        else:
            personal.plot(m)
    else:  # 対象が複数
        if g.params.rating:  # レーティング
            rating.plot(m)
        else:
            if g.params.order:
                summary.rank_plot(m)
            else:
                summary.point_plot(m)
