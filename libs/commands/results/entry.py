"""
libs/commands/results/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands.results import detail, summary, versus
from libs.domain.section import SubCommands
from libs.types import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class ResultsConfig(SubCommands):
    """
    成績集計サブコマンド（resultsセクション）の設定を管理するクラス。

    設定ファイルから成績コマンド固有のパラメータを読み込み、保持する役割を持つ。

    Attributes:
        default_commandword (str): コマンドのデフォルト起動文字列（"麻雀成績"）
        section (str): 設定ファイル内の対応するセクション名（CommandType.RESULTS の文字列値）

    """

    def __init__(self) -> None:
        """
        ResultsConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。

        """
        self.default_commandword: str = "麻雀成績"
        self.section: str = str(CommandType.RESULTS)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    成績集計処理のエントリーポイント。

    受信したメッセージデータを解析し、指定されたプレイヤーの有無、
    および各種フラグ（直接対戦マトリクス、スコア比較など）の優先順位に基づいて、
    適切な成績集計・表示関数へルーティングする。

    内部では、グローバルパラメータ（ ``g.params`` ）にメッセージから抽出したプレースホルダーの
    解析結果を展開して判定に使用する。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    Notes:
        Routing Logic:
            判定は以下の優先順位（上から順）で実行される。

            - **直接対戦（対戦マトリクス）**:
                ``versus_matrix`` かつ ``competition_list`` が指定されている場合。
                -> ``versus.aggregation`` を実行。
            - **スコア比較モード**:
                ``score_comparisons`` が指定されている場合。
                - ``statistics`` が有効: ``summary.statistics`` を実行。
                - ``statistics`` が無効: ``summary.difference`` を実行。
            - **成績詳細（単独モード）**:
                ``player_list`` の人数が1人の場合。
                -> ``detail.aggregation`` を実行。
            - **成績詳細（比較モード）**:
                ``statistics`` が有効 かつ ``player_list`` の人数が2人以上の場合。
                -> ``detail.comparison`` を実行。
            - **成績サマリ（通常モード）**:
                上記いずれにも該当しない場合。
                -> ``summary.aggregation`` を実行。

    """
    m.status.command_type = CommandType.RESULTS
    g.params = dictutil.placeholder(g.cfg.results, m)

    if g.params.versus_matrix and g.params.competition_list:
        versus.aggregation(m)  # 直接対戦
    elif g.params.score_comparisons:
        if g.params.statistics:
            summary.statistics(m)
        else:
            summary.difference(m)  # 成績サマリ(差分モード)
    elif len(g.params.player_list) == 1:
        detail.aggregation(m)  # 成績詳細(単独)
    elif g.params.statistics and len(g.params.player_list) > 1:
        detail.comparison(m)  # 成績詳細(比較)
    else:
        summary.aggregation(m)  # 成績サマリ(通常モード)
