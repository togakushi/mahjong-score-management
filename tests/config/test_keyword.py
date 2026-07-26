"""
設定ファイルから読み込むキーワード反映を検証するテスト。
"""

import sys
from typing import TYPE_CHECKING, cast

import pytest

import libs.global_value as g
from libs.bootstrap import configuration
from tests.config import param_data

if TYPE_CHECKING:
    from libs.domain.section import CommandClassType


@pytest.mark.parametrize(
    "parameter, config, word",
    list(param_data.keyword_test.values()),
    ids=list(param_data.keyword_test.keys()),
)
def test_dispatch_register(parameter: str, config: str, word: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    呼び出しキーワードが設定からディスパッチテーブルに反映されることを検証する。

    対象コマンドの commandword に期待語が含まれるかを確認する。

    Args:
        parameter (str): 確認対象のコマンド属性名。
        config (str): 読み込むテスト設定ファイル名。
        word (str): commandword に含まれるべき期待キーワード。
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", ["progname", f"--config=tests/test_data/{config}"])
    configuration.initialize(init_db=False)
    g.cfg.initialization()

    conf = cast("CommandClassType", getattr(g.cfg, parameter, ""))
    print("-->", conf)
    assert word in conf.commandwords_list
