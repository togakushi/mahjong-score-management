"""
設定値のデフォルト補完と初期状態を検証するテスト。
"""

import sys
from typing import TYPE_CHECKING

import pytest

import libs.global_value as g
from libs.bootstrap import configuration
from libs.commands.analysis import AnalysisConfig
from libs.commands.summary import SummaryConfig

if TYPE_CHECKING:
    from libs.domain.section import CommandClassType


def test_empty_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    空設定時に必須エイリアスが補完されることを検証する。

    最小構成ファイル読込後、主要スラッシュコマンドのエイリアスが欠落しないことを確認する。

    Args:
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/test_data/empty.ini"])
    configuration.initialize(init_db=False)

    # default alias
    assert "summary" in g.cfg.alias.summary
    assert "analysis" in g.cfg.alias.analysis
    assert "download" in g.cfg.alias.download
    assert "member" in g.cfg.alias.member
    assert "add" in g.cfg.alias.add
    assert "del" in g.cfg.alias.delete


@pytest.mark.parametrize("input_args", ["summary", "analysis"])
def test_subcommand_default(input_args: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    コマンド設定のデフォルト値が期待どおりであることを検証する。

    コマンド種別ごとの初期 commandword を含む主要パラメータを
    比較して回帰を防ぐ。

    Args:
        input_args (str): 検証対象のコマンド名。
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/test_data/empty.ini"])
    configuration.initialize(init_db=False)

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
        "comparisons": False,
        "statistics": False,
        "stipulated": 0,
        "stipulated_rate": 0.05,
        "unregistered_replace": True,
        "anonymous": False,
        "verbose": False,
        "versus": False,
        "collection": "",
        "always_argument": [],
        "target_mode": 0,
        "format": "",
        "filename": "",
        "interval": 80,
    }

    sub_command: CommandClassType
    match input_args:
        case "summary":
            sub_command = SummaryConfig()
            default.update(default_commandword="成績集計")
        case "analysis":
            sub_command = AnalysisConfig()
            default.update(default_commandword="成績分析")

    for k in sub_command.to_dict():
        if not default.get(k):
            continue
        assert sub_command.to_dict().get(k) == default.get(k)
