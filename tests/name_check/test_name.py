"""
メンバー名の許可/拒否パターン判定を検証するテスト。
"""

import sys
from typing import Any, Generator

import pytest

from libs.bootstrap import configuration
from libs.functions import lookup, validator
from tests.name_check import param_data

TEST_ARGS = ["progname", "--config=tests/test_data/saki.ini"]


@pytest.fixture(scope="module")
def parser_instance() -> Generator[None, Any, None]:
    """
    名前検証テストの共通初期化を行う。

    設定読込とメンバー一覧準備を実行し、検証関数の前提を整える。

    """
    old_argv = sys.argv[:]
    sys.argv = TEST_ARGS[:]

    configuration.setup(init_db=False)
    lookup.read_memberslist()

    yield

    sys.argv = old_argv


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_name_pattern_01.values()),
    ids=list(param_data.flag_name_pattern_01.keys()),
)
def test_name_permit(input_args: str, expected_flags: bool, parser_instance: Any) -> None:
    """
    登録許可パターンの名前判定結果を検証する。

    check_namepattern が True を返すべきケースで期待値と一致するか確認する。

    """
    flg, reason = validator.check_namepattern(input_args, "member")
    print(" -->", flg, reason)
    assert flg == expected_flags


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_name_pattern_02.values()),
    ids=list(param_data.flag_name_pattern_02.keys()),
)
def test_name_refusal(input_args: str, expected_flags: bool, parser_instance: Any) -> None:
    """
    登録拒否パターンの名前判定結果を検証する。

    check_namepattern が False を返すべきケースで期待値と一致するか確認する。

    """
    flg, _ = validator.check_namepattern(input_args, "member")
    assert flg == expected_flags
