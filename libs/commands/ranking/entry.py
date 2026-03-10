"""
libs/commands/ranking/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.bootstrap.section import SubCommands
from libs.commands.ranking import ranking, rating
from libs.domain.datamodels import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class RankingConfig(SubCommands):
    """rankingセクション処理"""

    def __init__(self):
        self.default_commandword: str = "麻雀ランキング"
        self.section: str = str(CommandType.RANKING)
        self.default_reset()


def main(m: "MessageParserProtocol"):
    """
    ランキング生成処理エントリーポイント

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    g.params = dictutil.placeholder(g.cfg.ranking, m)

    if g.params.get("rating"):  # レーティング
        m.status.command_type = CommandType.RATING
        rating.aggregation(m)
    else:  # ランキング
        m.status.command_type = CommandType.RANKING
        ranking.aggregation(m)
