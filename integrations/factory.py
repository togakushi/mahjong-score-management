"""
integrations/factory.py
"""

from typing import TYPE_CHECKING, Literal, NoReturn, TypeAlias, Union, overload

from integrations.discord.adapter import ServiceAdapter as discord_adapter
from integrations.slack.adapter import ServiceAdapter as slack_adapter
from integrations.standard_io.adapter import ServiceAdapter as std_adapter
from integrations.web.adapter import ServiceAdapter as web_adapter
from libs.types import ServiceType

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
def select_adapter(selected_service: Literal[ServiceType.SLACK], conf: "AppConfig") -> slack_adapter: ...


@overload
def select_adapter(selected_service: Literal[ServiceType.DISCORD], conf: "AppConfig") -> discord_adapter: ...


@overload
def select_adapter(selected_service: Literal[ServiceType.WEB], conf: "AppConfig") -> web_adapter: ...


@overload
def select_adapter(selected_service: Literal[ServiceType.STANDARD_IO], conf: "AppConfig") -> std_adapter: ...


@overload
def select_adapter(selected_service: Literal[ServiceType.UNKNOWN], conf: "AppConfig") -> NoReturn: ...


@overload
def select_adapter(selected_service: ServiceType, conf: "AppConfig") -> AdapterType: ...


def select_adapter(selected_service: ServiceType, conf: "AppConfig") -> AdapterType:
    """
    インターフェース選択

    Args:
        selected_service (ServiceType): 選択サービス
        conf (AppConfig): 設定ファイル

    Raises:
        ValueError: 未定義サービス

    Returns:
        AdapterType: アダプタインターフェース

    """
    match selected_service:
        case ServiceType.SLACK:
            return slack_adapter(conf.main_parser)
        case ServiceType.DISCORD:
            return discord_adapter(conf.main_parser)
        case ServiceType.WEB:
            return web_adapter(conf.main_parser)
        case ServiceType.STANDARD_IO:
            return std_adapter(conf.main_parser)
        case _:
            raise ValueError(f"Unknown service: {selected_service}")
