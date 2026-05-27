"""
libs/commands/ranking/entry.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands.ranking import ranking, rating
from libs.domain.section import SubCommands
from libs.types import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class RankingConfig(SubCommands):
    """
    ランキング出力サブコマンド（rankingセクション）の設定を管理するクラス。

    設定ファイルからランキングコマンド固有のパラメータを読み込み、保持する役割を持つ。

    Attributes:
        default_commandword (str): コマンドのデフォルト起動文字列（"麻雀ランキング"）
        section (str): 設定ファイル内の対応するセクション名（CommandType.RANKING の文字列値）

    """

    def __init__(self) -> None:
        """
        RankingConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。

        """
        self.default_commandword: str = "麻雀ランキング"
        self.section: str = str(CommandType.RANKING)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    ランキングおよびレーティング出力処理のエントリーポイント。

    受信したメッセージデータを解析し、レーティングオプションフラグの有無に応じて
    通常の成績ランキング（順位・ポイントなど）か、レーティングシステムの集計・出力かへ
    処理をルーティングする。

    内部では、グローバルパラメータ（ ``g.params`` ）にメッセージから抽出したプレースホルダーの
    解析結果を展開し、判定および出力内容の決定に使用する。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    Notes:
        Routing Logic:
            - **レーティングモード**:
                ``rating`` フラグが立っている場合。
                コマンドタイプを ``CommandType.RATING`` に設定し、 ``rating.aggregation`` を実行する。
            - **通常ランキングモード**:
                ``rating`` フラグがない（デフォルト）場合。
                コマンドタイプを ``CommandType.RANKING`` に設定し、 ``ranking.aggregation`` を実行する。

    """
    g.params = dictutil.placeholder(g.cfg.ranking, m)

    if g.params.rating:  # レーティング
        m.status.command_type = CommandType.RATING
        rating.aggregation(m)
    else:  # ランキング
        m.status.command_type = CommandType.RANKING
        ranking.aggregation(m)
