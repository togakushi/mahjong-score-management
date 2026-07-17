"""
integrations/standard_io/parser.py
"""

from datetime import datetime
from typing import Any, cast

from integrations.base.interface import MessageParserDataMixin, MessageParserInterface
from integrations.protocols import MsgData, PostData, StatusData
from libs.types import ChannelType, CommandType, MessageStatus


class MessageParser(MessageParserDataMixin, MessageParserInterface):
    """メッセージ解析クラス"""

    def __init__(self) -> None:
        """標準入出力メッセージ解析の初期状態を構築する。"""
        MessageParserDataMixin.__init__(self)
        self.data: MsgData = MsgData()
        self.post: PostData = PostData()
        self.status: StatusData = StatusData()
        self.COMMAND_TYPE = CommandType

    def parser(self, body: dict[str, Any]) -> None:
        self.data.status = MessageStatus.APPEND
        self.data.channel_id = "dummy"
        self.data.event_ts = str(datetime.now().timestamp())
        self.data.thread_ts = self.data.event_ts
        self.status.source = "standard_io"

        if body.get("event"):
            body = cast(dict[str, Any], body["event"])

        if body.get("text"):
            self.data.text = str(body.get("text", ""))
        else:
            self.data.text = ""

        if body.get("channel_name") == "directmessage":  # スラッシュコマンド扱い
            self.status.command_flg = True
            self.data.channel_type = ChannelType.DIRECT_MESSAGE
            self.data.channel_id = body.get("channel_id", "")

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
