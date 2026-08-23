"""
SQLテンプレートの構文整合性を検証するテスト。
"""

from pprint import pprint
from typing import Any

import pytest

from libs.domain.placeholder import PlaceholderBuilder

sql_tables: list[str] = [
    # 情報取得
    "GAME_INFO",
    "RESULTS_INFO",
    "MEMBER_INFO",
    "TEAM_INFO",
    "REMARKS_INFO",
    "RECORD_INFO",
    # 集計
    "SUMMARY_GAMEDATA",
    "SUMMARY_DETAILS",
    "SUMMARY_DETAILS2",
    "SUMMARY_RESULTS",
    "SUMMARY_CONSECUTIVE",
    "SUMMARY_TOTAL",
    "SUMMARY_VERSUS_MATRIX",
    "RANKING_RESULTS",
    "RANKING_RATINGS",
    "REPORT_PERSONAL_DATA",
    "REPORT_COUNT_DATA",
    "REPORT_GAME_STATISTICS",
    "REPORT_RESULTS_LIST",
    "REPORT_WINNER",
    "REPORT_MATRIX_TABLE",
    "REPORT_COUNT_MOVING",
    # その他
    "SELECT_ALL_RESULTS",
]
params_tables = {
    "guest_off": {"guest_skip": True},
    "guest_on": {"guest_skip": False},
    "guest_ignore": {"unregistered_replace": True},
    "team": {"individual": False},
    "team_with_friendly_fire": {"individual": False, "friendly_fire": False},
    "collection(daily)": {"collection": "daily"},
    "collection(weekly)": {"collection": "weekly"},
    "collection(monthly)": {"collection": "monthly"},
    "collection(yearly)": {"collection": "yearly"},
    "collection(all)": {"collection": "all"},
    "mode4": {"mode": 4},
    "mode3": {"mode": 3},
    "separate(True)": {"separate": True},
    "separate(False)": {"separate": False},
    "search_word": {"search_word": "find_word"},
    "group_length": {"group_length": 10},
    "target_player": {"target_player": ["player1", "player2"]},
    "all_player": {"all_player": False},
    "anonymous": {"anonymous": True},
    "ranked": {"ranked": 100},
    "reverse(True)": {"reverse": True},
    "reverse(False)": {"reverse": False},
    "stipulated": {"stipulated": 100},
    "stipulated_zero": {"stipulated": 0},
    "interval": {"interval": 100},
    "interval_zero": {"interval": 0},
    "target_count": {"target_count": 100},
    "target_count_zero": {"target_count": 0},
    "mixed": {"mixed": True},
    "mixed(False)_with_rule_set": {"mixed": False, "rule_list": ["dummy_rule1", "dummy_rule2"]},
    "mixed(True)_with_rule_set": {"mixed": True, "rule_list": ["dummy_rule1", "dummy_rule2"]},
    "aggregate_unit(M)": {"aggregate_unit": "M"},
    "aggregate_unit(Y)": {"aggregate_unit": "Y"},
    "aggregate_unit(A)": {"aggregate_unit": "A"},
    "aggregate_unit(_)": {"aggregate_unit": "X"},
    "undefined_word(0)": {"undefined_word": 0},
    "undefined_word(1)": {"undefined_word": 1},
    "undefined_word(2)": {"undefined_word": 2},
    "undefined_word(9)": {"undefined_word": 9},
    # "": {"": ""},
}

query_list = [pytest.param(name, id=name) for name in sql_tables]
param_list = [pytest.param(name, flags, id=name) for name, flags in params_tables.items()]


@pytest.mark.parametrize("param_name, flags", param_list)
@pytest.mark.parametrize("query_name", query_list)
def test_syntax_check(query_name: str, param_name: str, flags: dict[str, Any]) -> None:
    """
    SQL定義が各条件で読み出し可能であることを検証する。

    クエリ名とパラメータの全組み合わせでプレースホルダを評価し、
    構文崩れを検出する。

    Args:
        query_name (str): 実行対象のSQLテンプレート名。
        param_name (str): 適用するパラメータパターン名。
        flags (dict[str, Any]): プレースホルダへ反映する条件フラグ。

    """
    p = PlaceholderBuilder()
    p.update_from_dict(
        {
            "player_name": "dummy_player",
            "guest_name": "dummy_guest",
            "source": "dummy_source",
            "starttime": "1999-01-01 00:00:00",
            "endtime": "1999-01-01 00:00:00",
        }
    )
    p.update_from_dict(flags)
    p.database_file = "memdb1?mode=memory&cache=shared"

    pprint([query_name, param_name, p])
    _ = p.read_data(query_name)
