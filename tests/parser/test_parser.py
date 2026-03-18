"""
tests/parser/test_parser.py
"""

import sys
from typing import Any, Generator, cast

import pytest

import libs.global_value as g
from integrations import factory
from integrations.standard_io.adapter import ServiceAdapter
from libs.bootstrap import configuration
from libs.domain.command import CommandParser
from libs.types import ServiceType
from libs.utils import dictutil
from libs.utils.timekit import ExtendedDatetime as ExtDt
from tests.parser import param_data

TEST_ARGS = ["app.py", "--config=tests/test_data/saki.ini"]


@pytest.fixture(scope="module")
def parser_instance() -> Generator[ServiceAdapter, Any, None]:
    """初期化処理"""
    old_argv = sys.argv[:]
    sys.argv = TEST_ARGS[:]

    configuration.setup(init_db=False)

    adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)

    yield adapter

    sys.argv = old_argv


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_test_case_01.values()),
    ids=list(param_data.flag_test_case_01.keys()),
)
def test_flag_commands(input_args: str, expected_flags: dict[str, Any]) -> None:
    """1. フラグ系テスト"""
    parser = CommandParser()
    result = parser.analysis_argument(input_args.split())
    assert result.flags == expected_flags
    assert not result.unknown
    assert not result.search_range


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_test_case_02.values()),
    ids=list(param_data.flag_test_case_02.keys()),
)
def test_command_with_argument_int(input_args: str, expected_flags: dict[str, Any]) -> None:
    """2. 引数付きコマンド(数値)"""
    parser = CommandParser()
    result = parser.analysis_argument(input_args.split())

    print(f"\n  --> in: {input_args.split()} out: {result}")
    assert result.flags == expected_flags
    assert not result.unknown
    assert not result.search_range


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_test_case_03.values()),
    ids=list(param_data.flag_test_case_03.keys()),
)
def test_command_with_argument_str(input_args: str, expected_flags: dict[str, Any]) -> None:
    """3. 引数付きコマンド(文字)"""
    parser = CommandParser()
    result = parser.analysis_argument(input_args.split())

    print(f"\n  --> in: {input_args.split()} out: {result}")
    assert result.flags == expected_flags
    assert not result.unknown
    assert not result.search_range


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_test_case_04.values()),
    ids=list(param_data.flag_test_case_04.keys()),
)
def test_command_unknown_str(input_args: str, expected_flags: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """4. 不明なコマンド"""
    monkeypatch.setattr(sys, "argv", TEST_ARGS)
    configuration.setup()

    parser = CommandParser()
    g.params.unregistered_replace = False
    result = parser.analysis_argument(input_args.split())

    print(f"\n  --> in: {input_args.split()} out: {result}")
    assert not result.flags
    assert result.unknown == expected_flags
    assert not result.search_range


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_test_case_05.values()),
    ids=list(param_data.flag_test_case_05.keys()),
)
def test_command_date_range_str(input_args: str, expected_flags: list[ExtDt]) -> None:
    """5. 日付"""
    parser = CommandParser()
    result = parser.analysis_argument(input_args.split())

    print(f"\n  --> in: {input_args.split()} out: {result}")
    assert not result.flags
    assert not result.unknown
    assert not result.search_range == expected_flags


@pytest.mark.parametrize(
    "keyword, search_range",
    list(param_data.search_range.values()),
    ids=list(param_data.search_range.keys()),
)
def test_search_range(keyword: str, search_range: list[ExtDt], parser_instance: Any) -> None:
    """検索範囲"""
    m = cast(ServiceAdapter, parser_instance).parser()
    m.parser({"text": f"dummy_command {keyword}"})
    params = dictutil.placeholder(g.cfg.results, m)
    ret_range = [params.starttime, params.endtime]

    print(f"\n  --> in: {keyword.split()} out: {ret_range}")
    assert ret_range == search_range
