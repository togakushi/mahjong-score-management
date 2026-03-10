"""tests/parser/test_placeholder.py
"""

import sys

import pytest

import libs.global_value as g
from integrations import factory
from libs.bootstrap import configuration
from libs.data import lookup
from libs.utils import dictutil, formatter
from tests.parser import param_data

TEST_ARGS = ["progname", "--config=tests/test_data/saki.ini"]


@pytest.fixture(scope="module")
def parser_instance():
    """初期化処理"""
    old_argv = sys.argv[:]
    sys.argv = TEST_ARGS[:]

    configuration.setup(init_db=False)
    lookup.read_memberslist()

    adapter = factory.select_adapter("standard_io", g.cfg)

    yield adapter

    sys.argv = old_argv


@pytest.mark.parametrize(
    "input_args, player_name, player_list, competition_list",
    list(param_data.command_test_case_01.values()),
    ids=list(param_data.command_test_case_01.keys()),
)
def test_command_check(input_args, player_name, player_list, competition_list, parser_instance):
    """コマンド認識状態チェック"""
    m = parser_instance.parser()
    param = dictutil.placeholder(g.cfg.results, m)

    print(f"\n  --> in: {input_args.split()} out: {param}")
    assert param.get("player_name") == player_name
    assert param.get("player_list") == player_list
    assert param.get("competition_list") == competition_list


@pytest.mark.parametrize(
    "input_args, player_name, player_list, competition_list",
    list(param_data.name_test_case_01.values()),
    ids=list(param_data.name_test_case_01.keys()),
)
def test_player_check(input_args, player_name, player_list, competition_list, parser_instance):
    """プレイヤー名"""
    m = parser_instance.parser()
    m.parser({"text": f"{g.cfg.setting.keyword} {input_args}"})
    param = dictutil.placeholder(g.cfg.results, m)

    print(f"\n  --> in: {input_args.split()} out: {param}")
    assert param.get("player_name") == player_name
    assert param.get("player_list") == player_list
    assert param.get("competition_list") == competition_list


@pytest.mark.parametrize(
    "input_args, player_name, player_list, competition_list",
    list(param_data.team_saki_test_case.values()),
    ids=list(param_data.team_saki_test_case.keys()),
)
def test_team_check(input_args, player_name, player_list, competition_list, parser_instance):
    """チーム名"""
    m = parser_instance.parser()
    m.parser({"event": {"text": f"{g.cfg.setting.keyword} {input_args}"}})
    param = dictutil.placeholder(g.cfg.results, m)

    print(f"\n  --> in: {input_args.split()} out: {param}")
    assert param.get("player_name") == player_name
    assert param.get("player_list") == player_list
    assert param.get("competition_list") == competition_list


@pytest.mark.parametrize(
    "input_args, player_name, replace_name",
    list(param_data.guest_test_case.values()),
    ids=list(param_data.guest_test_case.keys()),
)
def test_guest_check(input_args, player_name, replace_name, parser_instance):
    """ゲストチェック"""
    m = parser_instance.parser()
    m.parser({"text": f"{g.cfg.setting.keyword} {input_args}"})
    g.params = dictutil.placeholder(g.cfg.results, m)

    parsed_name = str(g.params.get("player_name"))
    check_name = formatter.name_replace(parsed_name)

    assert parsed_name == player_name
    assert replace_name == check_name
