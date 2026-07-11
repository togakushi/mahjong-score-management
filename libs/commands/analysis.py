"""
libs/commands/analysis.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands import deliverables
from libs.domain.datamodels import CommandAttrs
from libs.domain.section import BaseSection
from libs.types import CommandType, DispatchRule
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol

COMMAND_DISPATCHER = [
    DispatchRule(
        "成績レポート",
        lambda: len(g.params.player_list) == 1 and g.params.report,
        deliverables.stats_report.gen_pdf,
    ),
    DispatchRule(
        "成績分析",
        lambda: len(g.params.player_list) == 1 and g.params.graph,
        deliverables.graph_personal.statistics_plot,
    ),
    DispatchRule(
        "レーティング推移グラフ",
        lambda: g.params.rating and g.params.graph,
        deliverables.graph_rating.plot,
    ),
    DispatchRule(
        "レーティング表",
        lambda: g.params.rating,
        deliverables.rating_calc.aggregation,
    ),
    DispatchRule(
        "順位素点相関図",
        lambda: g.params.raw_score and g.params.graph,
        deliverables.graph_regression.plot,
    ),
    DispatchRule(
        "素点分析",
        lambda: g.params.raw_score,
        deliverables.score_deviation.aggregation,
    ),
    DispatchRule(
        "ゲーム統計情報",
        lambda: g.params.statistics,
        deliverables.game_statistics.plot,
    ),
    DispatchRule(
        "対局対戦マトリクス",
        lambda: g.params.versus,
        deliverables.matrix.plot,
    ),
    DispatchRule(
        "成績詳細一覧",
        lambda: g.params.comparisons,
        deliverables.results_detail.stats_list,
    ),
    DispatchRule(
        "ランキング",
        lambda: True,
        deliverables.ranking_calc.aggregation,
    ),
]


class AnalysisConfig(BaseSection, CommandAttrs):
    """
    分析コマンド（analysisセクション）の設定を管理するクラス。

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

    def register(self) -> None:
        """ディスパッチャー登録"""
        for command in self.commandwords_list():
            g.keyword_dispatcher.update({command: main})
        if hasattr(g.cfg.alias, "analysis"):
            for command in g.cfg.alias.analysis:
                g.command_dispatcher.update({command: main})


def main(m: "MessageParserProtocol") -> None:
    """
    成績分析処理のエントリーポイント。

    受信したメッセージデータに基づいてパラメータを解析し、適切な成績分析関数へルーティングする。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    """
    g.params = dictutil.placeholder(g.cfg.analysis, m)
    for command in COMMAND_DISPATCHER:
        if command.condition():
            command.handler(m)
            break
