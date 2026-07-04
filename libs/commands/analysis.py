"""
libs/commands/analysis.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands import deliverables
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
    g.params = dictutil.placeholder(g.cfg.analysis, m)

    if len(g.params.player_list) == 1 and g.params.report:
        deliverables.stats_report.gen_pdf(m)
    elif len(g.params.player_list) == 1 and g.params.graph:
        deliverables.graph_personal.statistics_plot(m)
    else:
        if g.params.rating:  # レーティング
            if g.params.graph:
                deliverables.graph_rating.plot(m)
            else:
                deliverables.rating_calc.aggregation(m)
        elif g.params.raw_score:  # 素点分析
            if g.params.graph:
                deliverables.graph_regression.plot(m)
            else:
                deliverables.score_deviation.aggregation(m)
        elif g.params.report and g.params.statistics:
            deliverables.monthly.plot(m)
        else:
            if g.params.versus_matrix:  # 対局対戦マトリクス
                deliverables.matrix.plot(m)
            elif g.params.statistics:
                if not g.params.player_list:
                    if g.params.individual:
                        g.params.player_list = g.cfg.member.lists
                    else:
                        g.params.player_list = g.cfg.team.lists
                if g.params.graph:  # 成績詳細(比較)
                    deliverables.stats_list.main(m)
                else:
                    deliverables.detail.comparison(m)
            else:  # ランキング
                deliverables.ranking_calc.aggregation(m)
