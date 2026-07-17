"""
integrations/web/parser.py
"""

from typing import Any

from integrations.base.interface import MessageParserDataMixin, MessageParserInterface
from integrations.protocols import MsgData, PostData, StatusData
from libs.types import CommandType, MessageStatus


class MessageParser(MessageParserDataMixin, MessageParserInterface):
    """メッセージ解析クラス"""

    data: MsgData
    post: PostData
    status: StatusData

    def __init__(self) -> None:
        """Webメッセージ解析に必要な状態を初期化する。"""
        MessageParserDataMixin.__init__(self)
        self.data = MsgData()
        self.post = PostData()
        self.status = StatusData()
        self.COMMAND_TYPE = CommandType
        self.data.status = MessageStatus.APPEND
        self.status.command_flg = False

    def parser(self, body: dict[str, Any]) -> None:
        _ = body

    @property
    def in_thread(self) -> bool:
        return False

    @property
    def is_bot(self) -> bool:
        return False

    @property
    def check_updatable(self) -> bool:
        return True

    @property
    def ignore_user(self) -> bool:
        return False
