"""
tests/database/test_query_execution.py
"""

from dataclasses import asdict
from pprint import pprint
from typing import Any

import pytest

from libs.data import loader
from libs.domain.datamodels import CommandAttrs
from libs.types import PlaceholderDict

sql_tables: list[str] = {
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
    "SUMMARY_TOTAL",
    "SUMMARY_VERSUS_MATRIX",
    "RANKING_RESULTS",
    "RANKING_RATINGS",
    "REPORT_PERSONAL_DATA",
    "REPORT_COUNT_DATA",
    "REPORT_MONTHLY",
    "REPORT_RESULTS_LIST",
    "REPORT_WINNER",
    "REPORT_MATRIX_TABLE",
    "REPORT_COUNT_MOVING",
    #
    "SELECT_ALL_RESULTS",
    "SELECT_GAME_RESULTS",
}
params_tables = {
    "guest_off": {"guest_skip": True},
    "guest_on": {"guest_skip": False},
}

query_list = [pytest.param(name, id=name) for name in sql_tables]
param_list = [pytest.param(name, flags, id=name) for name, flags in params_tables.items()]


@pytest.mark.parametrize("param_name, flags", param_list)
@pytest.mark.parametrize("query_name", query_list)
def test_query_syntax(query_name: str, param_name: str, flags: dict[str, Any]):
    """xxxx"""
    params = {
        **asdict(CommandAttrs()),
        "ts": "1234567890.123456",
        "player_name": "dummy_player",
        "guest_name": "dummy_guest",
        "undefined_word": 1,
        "starttime": "1999-01-01 00:00:00",
        "endtime": "1999-01-01 00:00:00",
    }
    params.update(**flags)
    pprint([query_name, param_name, params])

    _ = loader.read_data(query_name, PlaceholderDict(params))
