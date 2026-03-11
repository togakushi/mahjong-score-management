"""
tests/events/test_message_dispatch.py
"""

import sys
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

import libs.dispatcher
import libs.global_value as g
from integrations import factory
from libs.bootstrap import configuration
from libs.domain.datamodels import MessageStatus
from tests.events import param_data

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def _init() -> "MessageParserProtocol":
    """初期化処理"""
    configuration.setup(init_db=False)
    adapter = factory.select_adapter("standard_io", g.cfg)
    m = adapter.parser()
    m.status.command_flg = True

    return m


@pytest.mark.parametrize(
    "module, config, keyword",
    list(param_data.message_event.values()),
    ids=list(param_data.message_event.keys()),
)
def test_keyword_event(module: str, config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """キーワード呼び出しテスト(サブコマンド)"""
    monkeypatch.setattr(sys, "argv", ["progname", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch(f"libs.bootstrap.configuration.libs.commands.{module}.entry.main") as mock_keyword_event,
    ):
        m = _init()
        m.data.text = keyword
        m.data.status = MessageStatus.APPEND
        m.status.command_flg = False

        libs.dispatcher.by_keyword(m)
        mock_keyword_event.assert_called_once()
