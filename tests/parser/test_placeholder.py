"""
placeholder 生成時の対象者抽出ロジックを検証するテスト。
"""

import sys
from typing import Any, Generator, cast

import pytest

import libs.global_value as g
from integrations import factory
from integrations.standard_io.adapter import ServiceAdapter
from libs.bootstrap import configuration
from libs.functions import lookup
from libs.types import ServiceType
from libs.utils import dictutil, textutil
from tests.parser import param_data

TEST_ARGS = ["progname", "--config=tests/test_data/saki.ini"]


@pytest.fixture(scope="module")
def parser_instance() -> Generator[ServiceAdapter, Any, None]:
    """
    Initialize a ServiceAdapter for placeholder tests.

    設定読込とメンバー一覧準備を行い、名前解決の前提を整える。

    """
    old_argv = sys.argv[:]
    sys.argv = TEST_ARGS[:]

    configuration.setup(init_db=False)
    lookup.read_memberslist()

    adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)

    yield adapter

    sys.argv = old_argv


@pytest.mark.parametrize(
    "input_args, player_name, player_list, competition_list",
    list(param_data.command_test_case_01.values()),
    ids=list(param_data.command_test_case_01.keys()),
)
def test_command_check(
    input_args: str,
    player_name: str,
    player_list: list[str],
    competition_list: list[str],
    parser_instance: Any,
) -> None:
    """
    コマンド解析後の対象者情報抽出結果を検証する。

    player_name/player_list/competition_list の各項目が期待値と一致するか確認する。

    """
    m = cast(ServiceAdapter, parser_instance).parser()
    param = dictutil.placeholder(g.cfg.results, m)

    print(f"\n  --> in: {input_args.split()} check: {player_name=}, {player_list=}, {competition_list=}")
    print(f"\n  --> out: {param}")
    assert param.player_name == player_name
    assert param.player_list == player_list
    assert param.competition_list == competition_list


@pytest.mark.parametrize(
    "input_args, player_name, player_list, competition_list",
    list(param_data.name_test_case_01.values()),
    ids=list(param_data.name_test_case_01.keys()),
)
def test_player_check(
    input_args: str,
    player_name: str,
    player_list: list[str],
    competition_list: list[str],
    parser_instance: Any,
) -> None:
    """
    プレイヤー名入力の解釈結果を検証する。

    ルールキーワード付き入力から抽出される対象者情報を照合する。

    """
    keyword = list(g.cfg.rule.keyword_mapping.keys())[0]
    m = cast(ServiceAdapter, parser_instance).parser()
    m.parser({"text": f"{keyword} {input_args}"})
    param = dictutil.placeholder(g.cfg.results, m)

    print(f"\n  --> in: {input_args.split()} out: {param}")
    assert param.player_name == player_name
    assert param.player_list == player_list
    assert param.competition_list == competition_list


@pytest.mark.parametrize(
    "input_args, player_name, player_list, competition_list",
    list(param_data.team_saki_test_case.values()),
    ids=list(param_data.team_saki_test_case.keys()),
)
def test_team_check(
    input_args: str,
    player_name: str,
    player_list: list[str],
    competition_list: list[str],
    parser_instance: Any,
) -> None:
    """
    チーム名入力の解釈結果を検証する。

    event.text 形式の入力でも対象者抽出が期待どおり動作するか確認する。

    """
    keyword = list(g.cfg.rule.keyword_mapping.keys())[0]
    m = cast(ServiceAdapter, parser_instance).parser()
    m.parser({"event": {"text": f"{keyword} {input_args}"}})
    param = dictutil.placeholder(g.cfg.results, m)

    print(f"\n  --> in: {input_args.split()} out: {param}")
    assert param.player_name == player_name
    assert param.player_list == player_list
    assert param.competition_list == competition_list


@pytest.mark.parametrize(
    "input_args, player_name, replace_name",
    list(param_data.guest_test_case.values()),
    ids=list(param_data.guest_test_case.keys()),
)
def test_guest_check(input_args: str, player_name: str, replace_name: str, parser_instance: Any) -> None:
    """
    ゲスト名入力時の解析名と置換表示名を検証する。

    placeholder の結果と name_replace 後の文字列が期待値に一致するか確認する。

    """
    keyword = list(g.cfg.rule.keyword_mapping.keys())[0]
    m = cast(ServiceAdapter, parser_instance).parser()
    m.parser({"text": f"{keyword} {input_args}"})
    g.params = dictutil.placeholder(g.cfg.results, m)

    parsed_name = g.params.player_name
    check_name = textutil.name_replace(parsed_name)

    assert parsed_name == player_name
    assert replace_name == check_name
