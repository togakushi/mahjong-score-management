"""
コマンド引数解析ロジックの動作を検証するテスト。
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
    """
    parser テスト用の ServiceAdapter を初期化する。

    テスト実行前後で sys.argv を退避・復元し、副作用を防止する。

    Args:
        None.

    Returns:
        Generator[ServiceAdapter, Any, None]: 初期化済みのServiceAdapterをyieldするジェネレータ。

    """
    old_argv = sys.argv[:]
    sys.argv = TEST_ARGS[:]

    configuration.initialize(init_db=False)

    adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)

    yield adapter

    sys.argv = old_argv


@pytest.mark.parametrize(
    "input_args, expected_flags",
    list(param_data.flag_test_case_01.values()),
    ids=list(param_data.flag_test_case_01.keys()),
)
def test_flag_commands(input_args: str, expected_flags: dict[str, Any]) -> None:
    """
    フラグ系入力の解析結果が期待どおりであることを検証する。

    flags の一致に加え、unknown と search_range が空であることを確認する。

    Args:
        input_args (str): 解析対象の入力文字列。
        expected_flags (dict[str, Any]): 期待するフラグ解析結果。

    """
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
    """
    数値引数付きコマンドの解析結果を検証する。

    想定された flags が生成され、余計な unknown/search_range がないことを確認する。

    Args:
        input_args (str): 解析対象の入力文字列。
        expected_flags (dict[str, Any]): 期待するフラグ解析結果。

    """
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
    """
    文字列引数付きコマンドの解析結果を検証する。

    文字列オプション解析が期待どおりの flags を返すことを確認する。

    Args:
        input_args (str): 解析対象の入力文字列。
        expected_flags (dict[str, Any]): 期待するフラグ解析結果。

    """
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
    """
    不明コマンド入力時の unknown 判定を検証する。

    未登録語置換を無効化した条件で unknown の抽出結果を照合する。

    Args:
        input_args (str): 解析対象の入力文字列。
        expected_flags (list[str]): 期待する unknown 抽出結果。
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", TEST_ARGS)
    configuration.initialize()

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
    """
    日付キーワード入力時の検索範囲解析を検証する。

    flags/unknown が空で、search_range が期待期間になることを確認する。

    Args:
        input_args (str): 解析対象の入力文字列。
        expected_flags (list[ExtDt]): 期待する期間オブジェクトのリスト。

    """
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
    """
    placeholder 生成時の検索範囲算出結果を検証する。

    キーワード入力から得た starttime/endtime が期待期間と一致するか確認する。

    Args:
        keyword (str): 検索範囲を表すキーワード。
        search_range (list[ExtDt]): 期待する開始・終了時刻のリスト。
        parser_instance (Any): 初期化済みのパーサフィクスチャ。

    """
    m = cast(ServiceAdapter, parser_instance).parser()
    m.parser({"text": f"dummy_command {keyword}"})
    params = dictutil.placeholder(g.cfg.summary, m)
    ret_range = [params.starttime, params.endtime]

    print(f"\n  --> in: {keyword.split()} out: {ret_range}")
    assert ret_range == search_range
