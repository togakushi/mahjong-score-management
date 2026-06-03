"""
libs/commands/graph/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands.graph import personal, rating, regression, summary
from libs.domain.section import SubCommands
from libs.types import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class GraphConfig(SubCommands):
    """
    グラフ描画サブコマンド（graphセクション）の設定を管理するクラス。

    設定ファイルからグラフコマンド固有のパラメータを読み込み、保持する役割を持つ。

    """

    def __init__(self) -> None:
        """
        GraphConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。

        """
        self.default_commandword: str = "麻雀グラフ"
        self.section: str = str(CommandType.GRAPH)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    グラフ生成・描画処理のエントリーポイント。

    受信したメッセージデータを解析し、指定されたプレイヤーの人数やオプションフラグ
    （統計、レーティング、順位など）の組み合わせに応じて、最適なグラフ描画関数へルーティングする。

    内部では、グローバルパラメータ（ ``g.params`` ）にメッセージから抽出したプレースホルダーの
    解析結果を展開して判定に使用する。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    Notes:
        Routing Logic:
            - **プレイヤーが1人の場合**:
                - ``statistics`` フラグあり: 個人統計グラフ（ ``personal.statistics_plot`` ）
                - フラグなし: 個人成績推移グラフ（ ``personal.plot`` ）
            - **プレイヤーが複数（2人以上）の場合**:
                - ``rating`` フラグあり: レーティング推移グラフ（ ``rating.plot`` ）
                - ``rating`` なし ＋ ``statistics`` フラグあり: 回帰分析グラフ（ ``regression.plot`` ）
                - ``rating`` なし ＋ ``statistics`` フラグなし ＋ ``order`` フラグあり: 複数人順位推移グラフ（ ``summary.rank_plot`` ）
                - ``rating`` なし ＋ ``statistics`` フラグなし ＋ ``order`` フラグなし: 複数人ポイント推移グラフ（ ``summary.point_plot`` ）

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
            if g.params.statistics:
                regression.plot(m)
            else:
                if g.params.order:
                    summary.rank_plot(m)
                else:
                    summary.point_plot(m)
