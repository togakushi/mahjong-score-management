"""
integrations/protocols.py
"""

from dataclasses import dataclass, field, fields, is_dataclass
from typing import TYPE_CHECKING, Any, Optional, Protocol

from libs.types import ActionStatus, ChannelType, CommandType, MessageStatus

if TYPE_CHECKING:
    from pathlib import Path  # noqa: F401

    import pandas as pd  # noqa: F401

    from libs.types import MessageType, StyleOptions


class DataMixin:
    """共通処理"""

    def reset(self) -> None:
        """デフォルト値にリセット"""
        if not is_dataclass(self):
            raise TypeError(f"{self.__class__.__name__} must be a dataclass")

        default = type(self)()
        for f in fields(self):
            setattr(self, f.name, getattr(default, f.name))


@dataclass
class MsgData(DataMixin):
    """入力情報管理クラス"""

    text: str = field(default=str())
    """本文"""
    event_ts: str = field(default="undetermined")
    """イベント発生タイムスタンプ"""
    thread_ts: str = field(default="undetermined")
    """スレッド元タイムスタンプ

    - *0*: スレッドになっていない
    - *undetermined*: 未定義状態
    """
    edited_ts: str = field(default="undetermined")
    """イベント編集タイムスタンプ"""
    channel_id: str = field(default=str())
    """チャンネルID"""
    channel_type: ChannelType = field(default=ChannelType.UNDETERMINED)
    """チャンネルタイプ"""
    user_id: str = field(default=str())
    """ユーザーID"""
    status: MessageStatus = field(default=MessageStatus.UNDETERMINED)
    """イベントステータス"""
    reaction_ok: list[str] = field(default_factory=list)
    """OKリアクションデータ格納用"""
    reaction_ng: list[str] = field(default_factory=list)
    """NGリアクションデータ格納用"""
    remarks: list[str] = field(default_factory=list)
    """メモ格納用"""


@dataclass
class PostData(DataMixin):
    """出力情報管理クラス"""

    headline: Optional[tuple["MessageType", "StyleOptions"]] = field(default=None)
    """ヘッダメッセージ"""
    message: list[tuple["MessageType", "StyleOptions"]] = field(default_factory=list)
    """本文メッセージ"""
    thread: bool = field(default=True)
    """スレッドに返す"""
    ts: str = field(default="undetermined")
    """指定タイムスタンプへの強制リプライ"""
    thread_title: str = field(default="")
    """スレッドに付けるタイトル"""


@dataclass
class StatusData(DataMixin):
    """処理状態管理クラス"""

    command_type: CommandType = field(default=CommandType.UNKNOWN)
    """実行(する/した)コマンド"""
    command_flg: bool = field(default=False)
    """コマンドとして実行されたかチェック

    - *True*: コマンド実行
    - *False*: キーワード呼び出し
    """
    command_name: str = field(default="")
    """実行したコマンド名"""

    reaction: bool = field(default=False)
    """データステータス状態

    - *True*: 矛盾なくデータを取り込んだ(OK)
    - *False*: 矛盾があったがデータを取り込んだ or データを取り込めなかった(NG)
    """
    action: ActionStatus = field(default=ActionStatus.NOTHING)
    """DBに対する操作"""
    target_ts: list[str] = field(default_factory=list)
    """同じ処理をしたタイムスタンプリスト(1件だけの処理でもセットされる)"""
    rpoint_sum: int = field(default=0)
    """素点合計値格納用"""

    result: bool = field(default=True)
    """メッセージデータに対する処理結果

    - *True*: 目的の処理が達成できた
    - *False*: 何らかの原因で処理が達成できなかった
    """
    message: Any = field(default=None)
    """汎用メッセージ"""
    source: str = field(default="")
    """データ入力元識別子"""


class MessageParserProtocol(Protocol):
    """メッセージ解析クラス"""

    data: MsgData
    """受け取ったメッセージデータ"""
    post: PostData
    """送信する内容"""
    status: StatusData
    """処理した結果"""

    COMMAND_TYPE: type[CommandType]
    """コマンドタイプ"""

    @property
    def in_thread(self) -> bool:
        """
        元メッセージへのリプライとなっているか

        Returns:
            bool:
                - *True*: リプライの形（リプライ／スレッドなど）
                - *False*: 通常メッセージ

        """

    @property
    def is_command(self) -> bool:
        """
        コマンドで実行されているかチェック

        Returns:
            bool:
                - *True*: コマンド実行
                - *False*: 非コマンド(キーワード呼び出し)

        """

    @property
    def is_bot(self) -> bool:
        """
        botによる操作かチェック

        Returns:
            bool:
                - *True*: botが操作
                - *False*: ユーザが操作

        """

    @property
    def keyword(self) -> str:
        """
        コマンドとして認識している文字列を返す。

        Returns:
            str: 認識済みのコマンドキーワード。

        """

    @property
    def argument(self) -> list[str]:
        """
        コマンド引数として認識しているオプションを返す。

        Returns:
            list[str]: 認識済みのオプション文字列リスト。

        """

    @property
    def reply_ts(self) -> str:
        """
        リプライ先のタイムスタンプを返す。

        Returns:
            str: 返信先メッセージのタイムスタンプ。

        """

    @property
    def check_updatable(self) -> bool:
        """
        DB更新可能チャンネルか判定する。

        Returns:
            bool:
                - *True*: 更新可能
                - *False*: 更新不可

        """

    @property
    def ignore_user(self) -> bool:
        """
        ignore_useridに存在するユーザかチェック

        Returns:
            bool:
                - *True*: 存在する(操作禁止ユーザ)
                - *False*: 存在しない

        """

    def set_headline(self, data: "MessageType", options: "StyleOptions") -> None:
        """ヘッドラインメッセージをセット"""

    def set_message(self, data: "MessageType", options: "StyleOptions") -> None:
        """本文メッセージをセット"""

    def delete_items(self, items: list[str]) -> None:
        """指定項目の削除"""

    def parser(self, body: Any) -> None:
        """メッセージ解析メソッド"""

    def reset(self) -> None:
        """状態リセット"""
