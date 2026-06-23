"""
config テストで利用するパラメータ定義。
"""

from typing import Any

# チャンネル内呼び出しキーワードデフォルト値
keyword_test: dict[str, tuple[Any, ...]] = {
    # parameter, config, word
    "summary: default": ("summary", "empty.ini", "成績集計"),
    "summary: override 1": ("summary", "commandword.ini", "集計コマンドの別名１"),
    "summary: override 2": ("summary", "commandword.ini", "集計コマンドの別名２"),
    "analysis: default": ("analysis", "empty.ini", "成績分析"),
    "analysis: override 1": ("analysis", "commandword.ini", "分析コマンドの別名１"),
    "analysis: override 2": ("analysis", "commandword.ini", "分析コマンドの別名２"),
}

# ヘルプキーワード
help_word: dict[str, tuple[Any, ...]] = {
    # config, word
    "help_default": ("empty.ini", "麻雀ヘルプ"),
    "help_override": ("commandword.ini", "ヘルプの別名"),
}
