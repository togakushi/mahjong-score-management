"""
integrations/factory.py
"""

from typing import TYPE_CHECKING, Literal, TypeAlias, Union, overload

from integrations.discord.adapter import ServiceAdapter as discord_adapter
from integrations.slack.adapter import ServiceAdapter as slack_adapter
from integrations.standard_io.adapter import ServiceAdapter as std_adapter
from integrations.web.adapter import ServiceAdapter as web_adapter

if TYPE_CHECKING:
    from libs.bootstrap.app_config import AppConfig

AdapterType: TypeAlias = Union[
    slack_adapter,
    discord_adapter,
    web_adapter,
    std_adapter,
]
"""アダプタインターフェース"""


@overload
def select_adapter(selected_service: Literal["slack"], conf: "AppConfig") -> slack_adapter: ...


@overload
def select_adapter(selected_service: Literal["discord"], conf: "AppConfig") -> discord_adapter: ...


@overload
def select_adapter(selected_service: Literal["web"], conf: "AppConfig") -> web_adapter: ...


@overload
def select_adapter(selected_service: Literal["standard_io"], conf: "AppConfig") -> std_adapter: ...


def select_adapter(selected_service: str, conf: "AppConfig") -> AdapterType:
    """
    インターフェース選択

    Args:
        selected_service (str): 選択サービス
        conf (AppConfig): 設定ファイル

    Raises:
        ValueError: 未定義サービス

    Returns:
        AdapterType: アダプタインターフェース

    """
    match selected_service:
        case "slack":
            return slack_adapter(conf.main_parser)
        case "discord":
            return discord_adapter(conf.main_parser)
        case "web":
            return web_adapter(conf.main_parser)
        case "standard_io":
            return std_adapter(conf.main_parser)
        case _:
            raise ValueError(f"Unknown service: {selected_service}")
