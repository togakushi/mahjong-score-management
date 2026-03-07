"""
tests/events/test_message_dispatch.py
"""

import sys
from unittest.mock import patch

import pytest

import libs.dispatcher
import libs.global_value as g
from integrations import factory
from integrations.protocols import MessageStatus
from libs.bootstrap import configuration
from tests.events import param_data


def _init():
    """初期化処理"""
    configuration.setup(init_db=False)
    adapter = factory.select_adapter("standard_io", g.cfg)
    m = adapter.parser()
    m.set_command_flag(True)

    return m


@pytest.mark.parametrize(
    "module, config, keyword",
    list(param_data.message_event.values()),
    ids=list(param_data.message_event.keys()),
)
def test_keyword_event(module, config, keyword, monkeypatch):
    """キーワード呼び出しテスト(サブコマンド)"""
    monkeypatch.setattr(sys, "argv", ["progname", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch(f"libs.bootstrap.configuration.libs.commands.{module}.entry.main") as mock_keyword_event,
    ):
        m = _init()
        m.data.text = keyword
        m.data.status = MessageStatus.APPEND
        m.set_command_flag(False)

        libs.dispatcher.by_keyword(m)
        mock_keyword_event.assert_called_once()
