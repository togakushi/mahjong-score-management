"""
libs/commands/help.py
"""

from typing import TYPE_CHECKING

import libs.global_value as g
from libs.commands.deliverables import text_assembly
from libs.domain.datamodels import CommandAttrs
from libs.domain.section import BaseSection
from libs.types import CommandType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class HelpConfig(BaseSection, CommandAttrs):
    """
    ヘルプ表示コマンド（helpセクション）の設定を管理するクラス。

    設定ファイルからヘルプコマンド固有のパラメータを読み込み、保持する役割を持つ。

    """

    def __init__(self) -> None:
        """
        HelpConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。
        """
        self.command_name: str = "ヘルプ"
        self.default_commandword: str = "麻雀ヘルプ"
        self.section: str = str(CommandType.HELP)
        self.default_reset()

    def register(self) -> None:
        """
        ディスパッチャー登録。

        ヘルプコマンドの呼び出しワードをディスパッチャーテーブルに登録する。

        """
        for command in self.commandwords_list():
            g.keyword_dispatcher.update({command: main})


def main(m: "MessageParserProtocol") -> None:
    """
    ヘルプ処理のエントリーポイント。

    受信したメッセージデータに基づいてヘルプパラメータを解析し、ユーザー向けのヘルプ案内メッセージを構築する。
    メッセージの送信スレッドのタイトルやタイムスタンプなどの投稿メタデータもここで設定される。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    """
    g.params = dictutil.placeholder(g.cfg.help, m)

    text_assembly.help_message(m)

    m.post.ts = m.data.event_ts
    m.post.thread_title = "ヘルプメッセージ"
