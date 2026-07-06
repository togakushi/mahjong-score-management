"""
libs/commands/summary.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands import deliverables
from libs.domain.section import SubCommands
from libs.types import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class SummaryConfig(SubCommands):
    """
    集計コマンド（summaryセクション）の設定を管理するクラス。

    設定ファイルから集計コマンド固有のパラメータを読み込み、保持する役割を持つ。

    """

    def __init__(self) -> None:
        """
        SummaryConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。
        """
        self.default_commandword: str = "成績集計"
        self.section: str = str(CommandType.SUMMARY)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    成績分析処理のエントリーポイント。

    受信したメッセージデータに基づいてパラメータを解析し、適切な成績集計関数へルーティングする。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    """
    g.params = dictutil.placeholder(g.cfg.summary, m)

    if len(g.params.player_list) == 1:  # 対象が単独
        if g.params.graph:
            deliverables.graph_personal.plot(m)
        else:
            deliverables.results_detail.aggregation(m)  # 成績詳細
    else:  # 対象が複数
        if g.params.order:
            if g.params.graph:
                deliverables.graph_summary.rank_plot(m)  # 順位変動
            else:
                deliverables.winner.plot(m)  # 成績上位
        elif g.params.versus_matrix and g.params.competition_list:
            deliverables.versus.aggregation(m)  # 直接対戦
        elif g.params.score_comparisons:
            deliverables.results_summary.difference(m)  # 成績サマリ(差分モード)
        else:
            if g.params.graph:
                deliverables.graph_summary.point_plot(m)  # ポイント推移
            else:
                deliverables.results_summary.aggregation(m)  # 成績サマリ(通常モード)
