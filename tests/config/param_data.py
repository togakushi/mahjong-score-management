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
    "summary: combination 1": ("summary", "combination1.ini", "テストルール集計１"),
    "summary: combination 2": ("summary", "combination1.ini", "テストルール集計２"),
    "summary: combination 3": ("summary", "combination2.ini", "追加ルール１集計３"),
    "summary: combination 4": ("summary", "combination2.ini", "追加ルール２集計３"),
    "analysis: default": ("analysis", "empty.ini", "成績分析"),
    "analysis: override 1": ("analysis", "commandword.ini", "分析コマンドの別名１"),
    "analysis: override 2": ("analysis", "commandword.ini", "分析コマンドの別名２"),
    "analysis: combination 1": ("analysis", "combination1.ini", "テストルール分析１"),
    "analysis: combination 2": ("analysis", "combination1.ini", "テストルール分析２"),
    "help: default": ("help", "empty.ini", "麻雀ヘルプ"),
    "help: override": ("help", "commandword.ini", "ヘルプの別名"),
    "help: combination 1": ("help", "combination1.ini", "テストルールヘルプ１"),
    "help: combination 2": ("help", "combination1.ini", "テストルールヘルプ２"),
    "member: default": ("member", "empty.ini", "メンバー一覧"),
    "member: override": ("member", "commandword.ini", "メンバー一覧の別名"),
    "member: combination 1": ("member", "combination1.ini", "テストルールメンバー１"),
    "member: combination 2": ("member", "combination1.ini", "テストルールメンバー２"),
    "team: default": ("team", "empty.ini", "チーム一覧"),
    "team: override": ("team", "commandword.ini", "チーム一覧の別名"),
    "team: combination 1": ("team", "combination1.ini", "テストルールチーム１"),
    "team: combination 2": ("team", "combination1.ini", "テストルールチーム２"),
}
