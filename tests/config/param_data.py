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
    "summary: combination 1": ("summary", "combination.ini", "テストルール集計組合１"),
    "summary: combination 2": ("summary", "combination.ini", "テストルール集計組合２"),
    "analysis: default": ("analysis", "empty.ini", "成績分析"),
    "analysis: override 1": ("analysis", "commandword.ini", "分析コマンドの別名１"),
    "analysis: override 2": ("analysis", "commandword.ini", "分析コマンドの別名２"),
    "analysis: combination 1": ("analysis", "combination.ini", "テストルール分析組合１"),
    "analysis: combination 2": ("analysis", "combination.ini", "テストルール分析組合２"),
    "help: default": ("help", "empty.ini", "麻雀ヘルプ"),
    "help: override": ("help", "commandword.ini", "ヘルプの別名"),
    "help: combination 1": ("help", "combination.ini", "テストルールヘルプ組合１"),
    "help: combination 2": ("help", "combination.ini", "テストルールヘルプ組合２"),
    "member: default": ("member", "empty.ini", "メンバー一覧"),
    "member: override": ("member", "commandword.ini", "メンバー一覧の別名"),
    "member: combination 1": ("member", "combination.ini", "テストルールメンバー組合１"),
    "member: combination 2": ("member", "combination.ini", "テストルールメンバー組合２"),
    "team: default": ("team", "empty.ini", "チーム一覧"),
    "team: override": ("team", "commandword.ini", "チーム一覧の別名"),
    "team: combination 1": ("team", "combination.ini", "テストルールチーム組合１"),
    "team: combination 2": ("team", "combination.ini", "テストルールチーム組合２"),
}
