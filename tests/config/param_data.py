"""
テスト用パラメータ
"""

from typing import Any

# チャンネル内呼び出しキーワードデフォルト値
keyword_test: dict[str, tuple[Any, ...]] = {
    # parameter, config, word
    "results_default": ("results", "empty.ini", "麻雀成績"),
    "results_override1": ("results", "commandword.ini", "麻雀成績の別名１"),
    "results_override2": ("results", "commandword.ini", "麻雀成績の別名２"),
    "graph_default": ("graph", "empty.ini", "麻雀グラフ"),
    "graph_override": ("graph", "commandword.ini", "麻雀グラフの別名"),
    "ranking_default": ("ranking", "empty.ini", "麻雀ランキング"),
    "ranking_override": ("ranking", "commandword.ini", "麻雀ランキングの別名"),
    "report_default": ("report", "empty.ini", "麻雀レポート"),
    "report_override": ("report", "commandword.ini", "麻雀レポートの別名"),
}

# ヘルプキーワード
help_word: dict[str, tuple[Any, ...]] = {
    # config, word
    "help_default": ("empty.ini", "麻雀ヘルプ"),
    "help_override": ("commandword.ini", "ヘルプの別名"),
}
