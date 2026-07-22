"""
メッセージイベントのキーワードディスパッチを検証するテスト。
"""

import sys
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

import libs.dispatcher
import libs.global_value as g
from integrations import factory
from libs.bootstrap import configuration
from libs.types import MessageStatus, ServiceType
from tests.events import param_data

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def _init() -> "MessageParserProtocol":
    """
    メッセージディスパッチ用パーサを初期化する。

    標準入出力アダプタを生成し、コマンド判定フラグを事前設定する。

    Args:
        None.

    Returns:
        MessageParserProtocol: 初期化済みのメッセージパーサ。

    """
    configuration.setup(init_db=False)
    adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)
    m = adapter.parser()
    m.status.command_flg = True

    return m


@pytest.mark.parametrize(
    "module, config, keyword",
    list(param_data.message_event.values()),
    ids=list(param_data.message_event.keys()),
)
def test_keyword_event(module: str, config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    キーワード入力で対象コマンドがディスパッチテーブルから呼び出されることを検証する。

    設定とイベント状態を与えて dispatcher を実行し、対応エントリ関数の呼び出し回数を確認する。

    Args:
        module (str): モック対象とするコマンドモジュール名。
        config (str): 読み込むテスト設定ファイル名。
        keyword (str): 入力するコマンドキーワード。
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", ["progname", "--service=std", f"--config=tests/test_data/{config}"])

    with (
        patch(f"libs.commands.{module}") as mock_keyword_event,
    ):
        m = _init()
        m.data.text = keyword
        m.data.status = MessageStatus.APPEND
        m.status.command_flg = False

        libs.dispatcher.by_keyword(m)
        mock_keyword_event.assert_called_once()
