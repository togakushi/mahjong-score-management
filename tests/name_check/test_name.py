"""tests/name_check/test_name.py
"""

import sys

import pytest

from libs.bootstrap import configuration
from libs.data import lookup
from libs.utils import validator
from tests.name_check import param_data

TEST_ARGS = ["progname", "--config=tests/test_data/saki.ini"]


@pytest.fixture(scope="module")
def parser_instance():
    """初期化処理"""
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
def test_name_permit(input_args, expected_flags, parser_instance):
    """メンバー登録テスト(OK)"""
    flg, reason = validator.check_namepattern(input_args, "member")
    print(" -->", flg, reason)
    assert flg == expected_flags


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_name_pattern_02.values()),
    ids=list(param_data.flag_name_pattern_02.keys()),
)
def test_name_refusal(input_args, expected_flags, parser_instance):
    """メンバー登録テスト(NG)"""
    flg, _ = validator.check_namepattern(input_args, "member")
    assert flg == expected_flags
