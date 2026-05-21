"""
tests/config/test_keyword.py
"""

import sys
from typing import TYPE_CHECKING, cast

import pytest

import libs.global_value as g
from libs.bootstrap import configuration
from tests.config import param_data

if TYPE_CHECKING:
    from libs.domain.section import SubCommands


@pytest.mark.parametrize(
    "parameter, config, word",
    list(param_data.keyword_test.values()),
    ids=list(param_data.keyword_test.keys()),
)
def test_keyword(parameter: str, config: str, word: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """呼び出しキーワード取り込みチェック"""
    monkeypatch.setattr(sys, "argv", ["progname", f"--config=tests/testdata/{config}"])
    configuration.setup(init_db=False)

    conf = cast("SubCommands", getattr(g.cfg, parameter, ""))
    assert word in conf.commandword


@pytest.mark.parametrize(
    "config, word",
    list(param_data.help_word.values()),
    ids=list(param_data.help_word.keys()),
)
def test_help(config: str, word: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """ヘルプキーワード取り込みチェック"""
    monkeypatch.setattr(sys, "argv", ["progname", f"--config=tests/testdata/{config}"])
    configuration.setup(init_db=False)

    assert word in g.cfg.help.commandword
