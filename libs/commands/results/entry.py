"""
libs/commands/results/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.bootstrap.section import SubCommands
from libs.commands.results import detail, summary, versus
from libs.domain.datamodels import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class ResultsConfig(SubCommands):
    """resultsセクション処理"""

    def __init__(self):
        self.default_commandword: str = "麻雀成績"
        self.section: str = str(CommandType.RESULTS)
        self.default_reset()


def main(m: "MessageParserProtocol"):
    """成績集計処理エントリーポイント

    Args:
        m (MessageParserProtocol): メッセージデータ
    """

    m.status.command_type = CommandType.RESULTS
    g.params = dictutil.placeholder(g.cfg.results, m)

    if g.params.get("versus_matrix", False) and g.params["competition_list"]:
        versus.aggregation(m)  # 直接対戦
    elif g.params.get("score_comparisons", False):
        summary.difference(m)  # 成績サマリ(差分モード)
    elif g.params["competition_list"]:
        detail.comparison(m)  # 成績詳細(比較)
    elif g.params["player_list"]:
        detail.aggregation(m)  # 成績詳細(単独)
    else:
        summary.aggregation(m)  # 成績サマリ(通常モード)
