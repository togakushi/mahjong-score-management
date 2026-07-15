"""
libs/commands/summary.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands import deliverables
from libs.domain.datamodels import CommandAttrs
from libs.domain.section import BaseSection
from libs.types import DispatchRule
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol

COMMAND_DISPATCHER = [
    DispatchRule(
        "成績グラフ",
        lambda: len(g.params.player_list) == 1 and g.params.graph,
        deliverables.graph_personal.plot,
    ),
    DispatchRule(
        "成績詳細",
        lambda: len(g.params.player_list) == 1,
        deliverables.results_detail.aggregation,
    ),
    DispatchRule(
        "順位変動グラフ",
        lambda: g.params.order and g.params.graph,
        deliverables.graph_summary.rank_plot,
    ),
    DispatchRule(
        "通算ポイント推移グラフ",
        lambda: g.params.graph,
        deliverables.graph_summary.point_plot,
    ),
    DispatchRule(
        "成績上位者",
        lambda: g.params.order,
        deliverables.winner.plot,
    ),
    DispatchRule(
        "直接対戦結果",
        lambda: bool(g.params.competition_list) and bool(g.params.player_list) and g.params.versus,
        deliverables.versus.aggregation,
    ),
    DispatchRule(
        "成績サマリ表（差分）",
        lambda: g.params.comparisons,
        deliverables.results_summary.difference,
    ),
    DispatchRule(
        "成績サマリ表（全体）",
        lambda: True,
        deliverables.results_summary.aggregation,
    ),
]


class SummaryConfig(BaseSection, CommandAttrs):
    """
    集計コマンド（summaryセクション）の設定を管理するクラス。

    設定ファイルから集計コマンド固有のパラメータを読み込み、保持する役割を持つ。

    """

    def __init__(self) -> None:
        """
        SummaryConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。
        """
        self.command_name: str = "集計コマンド"
        self.default_commandword: str = "成績集計"
        self.section: str = "summary"
        self.default_reset()

    def register(self) -> None:
        """
        ディスパッチャー登録。

        集計コマンドの呼び出しワードをディスパッチャーテーブルに登録する。

        """
        for command in self.commandwords_list():
            g.keyword_dispatcher.update({command: main})
        if hasattr(g.cfg.alias, "summary"):
            for command in g.cfg.alias.summary:
                g.command_dispatcher.update({command: main})


def main(m: "MessageParserProtocol") -> None:
    """
    成績分析処理のエントリーポイント。

    受信したメッセージデータに基づいてパラメータを解析し、適切な成績集計関数へディスパッチする。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    """
    g.params = dictutil.placeholder(g.cfg.summary, m)
    for command in COMMAND_DISPATCHER:
        if command.condition():
            command.handler(m)
            break
