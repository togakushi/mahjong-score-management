"""
libs/commands/report/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from integrations.protocols import CommandType
from libs.bootstrap.section import SubCommands
from libs.commands.report import matrix, monthly, stats_list, stats_report, winner
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class ReportConfig(SubCommands):
    """reportセクション処理"""

    def __init__(self):
        self.default_commandword = "麻雀レポート"
        self.section = "report"
        self.default_reset()


def main(m: "MessageParserProtocol"):
    """レポート生成処理エントリーポイント

    Args:
        m (MessageParserProtocol): メッセージデータ
    """

    m.status.command_type = CommandType.REPORT
    g.params = dictutil.placeholder(g.cfg.report, m)

    if len(g.params["player_list"]) == 1:  # 成績レポート
        stats_report.gen_pdf(m)
    elif g.params.get("order"):
        winner.plot(m)
    elif g.params.get("statistics"):
        monthly.plot(m)
    elif g.params.get("versus_matrix") or len(g.params["player_list"]) >= 2:  # 対局対戦マトリックス
        matrix.plot(m)
    else:
        stats_list.main(m)
