"""
libs/commands/analysis/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain import deliverables
from libs.domain.section import SubCommands
from libs.types import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class AnalysisConfig(SubCommands):
    """
    分析サブコマンド（analysisセクション）の設定を管理するクラス。

    設定ファイルから分析コマンド固有のパラメータを読み込み、保持する役割を持つ。

    """

    def __init__(self) -> None:
        """
        AnalysisConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。
        """
        self.default_commandword: str = "成績分析"
        self.section: str = str(CommandType.ANALYSIS)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    成績分析処理のエントリーポイント。

    受信したメッセージデータに基づいてパラメータを解析し、適切な成績分析関数へルーティングする。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    """
    m.status.command_type = CommandType.ANALYSIS
    g.params = dictutil.placeholder(g.cfg.analysis, m)

    if len(g.params.player_list) == 1 and g.params.report:
        m.status.command_type = CommandType.REPORT
        deliverables.graph_personal.statistics_plot(m)
    elif len(g.params.player_list) == 1 and g.params.graph:
        m.status.command_type = CommandType.GRAPH
        deliverables.graph_personal.statistics_plot(m)
    else:
        if g.params.rating:  # レーティング
            if g.params.graph:
                m.status.command_type = CommandType.GRAPH
                deliverables.graph_rating.plot(m)
            else:
                m.status.command_type = CommandType.RATING
                deliverables.rating_calc.aggregation(m)
        elif g.params.raw_score:  # 素点分析
            if g.params.graph:
                m.status.command_type = CommandType.GRAPH
                deliverables.graph_regression.plot(m)
            else:
                m.status.command_type = CommandType.RANKING
                deliverables.score_deviation.aggregation(m)
        elif g.params.report and g.params.statistics:
            m.status.command_type = CommandType.REPORT
            deliverables.monthly.plot(m)
        else:
            if g.params.versus_matrix:  # 対局対戦マトリックス
                deliverables.matrix.plot(m)
            elif g.params.statistics:
                if not g.params.player_list:
                    if g.params.individual:
                        g.params.player_list = g.cfg.member.lists
                    else:
                        g.params.player_list = g.cfg.team.lists
                if g.params.graph:  # 成績詳細(比較)
                    m.status.command_type = CommandType.REPORT
                    deliverables.stats_list.main(m)
                else:
                    m.status.command_type = CommandType.SUMMARY
                    deliverables.detail.comparison(m)
            else:  # ランキング
                m.status.command_type = CommandType.RANKING
                deliverables.ranking_calc.aggregation(m)
