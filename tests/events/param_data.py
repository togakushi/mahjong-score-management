"""
events テストで利用する疑似イベントデータ定義。
"""

from typing import Any, TypedDict

from slack_bolt import App


class FakeBodyDict(TypedDict, total=False):
    """
    イベントテスト用の疑似Body構造を表す型。

    最小限のキーだけで柔軟にテストできるよう total=False で定義する。

    """

    command: str
    type: str
    event: dict[str, str]


FAKE_CLIENT = App.client

FAKE_BODY: FakeBodyDict = {
    "command": "/mahjong",
    "event": {
        "channel_name": "directmessage",
        "user": "U9999999999",
        "type": "message",
        "ts": "1234567890.123456",
        "thread_ts": "1234567890.123456",
    },
}

message_help: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "麻雀成績ヘルプ"),
    "over ride": ("commandword.ini", "ヘルプの別名"),
    "double word": ("empty.ini", "麻雀成績ヘルプ 未定義ワード"),
}

message_event: dict[str, tuple[Any, ...]] = {
    # module, config, keyword
    "summary: default": ("summary", "empty.ini", "成績集計"),
    "summary: over ride": ("summary", "commandword.ini", "集計コマンドの別名１"),
    "summary: double word": ("summary", "empty.ini", "成績集計 未定義ワード"),
    "analysis: default": ("analysis", "empty.ini", "成績分析"),
    "analysis: over ride": ("analysis", "commandword.ini", "分析コマンドの別名１"),
    "analysis: double word": ("analysis", "empty.ini", "成績分析 未定義ワード"),
}

slash_help: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "help"),
    "double word": ("empty.ini", "help xxx"),
    "unknown": ("empty.ini", "xxx"),
}

slash_check: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "check"),
    "alias": ("commandword.ini", "チェックのエイリアス"),
    "double word": ("empty.ini", "check xxx"),
}

slash_download: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "download"),
    "alias": ("commandword.ini", "ダウンロード"),
    "double word": ("empty.ini", "download xxx"),
}

slash_member_list: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "member"),
    "alias": ("commandword.ini", "メンバー一覧"),
    "double word": ("empty.ini", "member xxx"),
}

slash_member_add: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "add"),
    "alias 01": ("commandword.ini", "メンバー追加"),
    "alias 02": ("commandword.ini", "入部届"),
    "double word": ("empty.ini", "add xxx"),
}

slash_member_del: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default 01": ("empty.ini", "del"),
    "alias 01": ("commandword.ini", "メンバー削除"),
    "alias 02": ("commandword.ini", "退部届"),
    "double word": ("empty.ini", "del xxx"),
}

slash_team_create: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "team_create"),
}

slash_team_del: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "team_del"),
}

slash_team_add: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "team_add"),
}

slash_team_remove: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "team_remove"),
}

slash_team_list: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "team_list"),
}

slash_team_clear: dict[str, tuple[Any, ...]] = {
    # config, keyword
    "default": ("empty.ini", "team_clear"),
}
