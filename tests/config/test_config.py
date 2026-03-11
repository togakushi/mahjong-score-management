"""
tests/config/test_config.py
"""

import sys
from typing import TYPE_CHECKING

import pytest

import libs.global_value as g
from libs.bootstrap import configuration
from libs.commands.graph.entry import GraphConfig
from libs.commands.help.entry import HelpConfig
from libs.commands.ranking.entry import RankingConfig
from libs.commands.report.entry import ReportConfig
from libs.commands.results.entry import ResultsConfig

if TYPE_CHECKING:
    from libs.bootstrap.section import SubCommands


def test_empty_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """空設定チェック"""
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/testdata/empty.ini"])
    configuration.setup(init_db=False)

    assert g.cfg.mahjong.origin_point == 250
    assert g.cfg.mahjong.return_point == 300

    # default alias
    assert "results" in g.cfg.alias.results
    assert "graph" in g.cfg.alias.graph
    assert "ranking" in g.cfg.alias.ranking
    assert "report" in g.cfg.alias.report
    assert "download" in g.cfg.alias.download
    assert "member" in g.cfg.alias.member
    assert "add" in g.cfg.alias.add
    assert "del" in g.cfg.alias.delete


@pytest.mark.parametrize("input_args", ["results", "graph", "ranking", "report", "help"])
def test_subcommand_default(input_args: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """サブコマンドデフォルト値チェック"""
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/testdata/empty.ini"])
    configuration.setup(init_db=False)

    default = {
        "section": input_args,
        "default_commandword": "",
        "commandword": [],
        "command_suffix": [],
        "aggregation_range": "当日",
        "individual": True,
        "all_player": False,
        "daily": True,
        "fourfold": True,
        "game_results": False,
        "guest_skip": True,
        "guest_skip2": True,
        "ranked": 3,
        "score_comparisons": False,
        "statistics": False,
        "stipulated": 0,
        "stipulated_rate": 0.05,
        "unregistered_replace": True,
        "anonymous": False,
        "verbose": False,
        "versus_matrix": False,
        "collection": "",
        "always_argument": [],
        "target_mode": 0,
        "format": "",
        "filename": "",
        "interval": 80,
    }

    sub_command: SubCommands
    match input_args:
        case "results":
            sub_command = ResultsConfig()
            default.update(default_commandword="麻雀成績")
        case "graph":
            sub_command = GraphConfig()
            default.update(default_commandword="麻雀グラフ")
        case "ranking":
            sub_command = RankingConfig()
            default.update(default_commandword="麻雀ランキング")
        case "report":
            sub_command = ReportConfig()
            default.update(default_commandword="麻雀レポート")
        case "help":
            sub_command = HelpConfig()
            default.update(default_commandword="麻雀ヘルプ")

    assert sub_command.to_dict() == default
