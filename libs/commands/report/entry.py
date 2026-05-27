"""
libs/commands/report/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands.report import matrix, monthly, stats_list, stats_report, winner
from libs.domain.section import SubCommands
from libs.types import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class ReportConfig(SubCommands):
    """
    レポート生成サブコマンド（reportセクション）の設定を管理するクラス。

    設定ファイルからレポートコマンド固有のパラメータを読み込み、保持する役割を持つ。

    Attributes:
        default_commandword (str): コマンドのデフォルト起動文字列（"麻雀レポート"）
        section (str): 設定ファイル内の対応するセクション名（CommandType.REPORT の文字列値）

    """

    def __init__(self) -> None:
        """
        ReportConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。

        """
        self.default_commandword: str = "麻雀レポート"
        self.section: str = str(CommandType.REPORT)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    レポート生成・出力処理のエントリーポイント。

    受信したメッセージデータを解析し、指定されたプレイヤーの人数や各種オプションフラグの
    組み合わせ（優先順位順）に応じて、適切なレポート出力関数へルーティングする。

    内部では、グローバルパラメータ（ ``g.params`` ）にメッセージから抽出したプレースホルダーの
    解析結果を展開して条件判定に使用する。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    Notes:
        Routing Logic:
            探索は以下の条件分岐の優先順位（上から順に判定）に従って実行される。

            - **個人成績詳細レポート (PDF出力)**:
                ``player_list`` （対象プレイヤー）がちょうど1人指定されている場合。
                -> ``stats_report.gen_pdf`` を実行。
            - **勝者・順位推移レポート**:
                ``order`` フラグが立っている場合（かつプレイヤー指定が1人ではない場合）。
                -> ``winner.plot`` を実行。
            - **月間・統計レポート**:
                ``statistics`` フラグが立っている場合。
                -> ``monthly.plot`` を実行。
            - **対局対戦マトリックスレポート**:
                ``versus_matrix`` フラグが立っている、または ``player_list`` に2人以上のプレイヤーが指定されている場合。
                -> ``matrix.plot`` を実行。
            - **成績一覧レポート (デフォルト挙動)**:
                上記のいずれの条件にも該当しない場合。
                -> ``stats_list.main`` を実行し、テキストベースまたは標準の成績一覧を出力。
    """
    m.status.command_type = CommandType.REPORT
    g.params = dictutil.placeholder(g.cfg.report, m)

    if len(g.params.player_list) == 1:  # 成績レポート
        stats_report.gen_pdf(m)
    elif g.params.order:
        winner.plot(m)
    elif g.params.statistics:
        monthly.plot(m)
    elif g.params.versus_matrix or len(g.params.player_list) >= 2:  # 対局対戦マトリックス
        matrix.plot(m)
    else:
        stats_list.main(m)
