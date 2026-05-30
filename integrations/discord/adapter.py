"""
integrations/discord/adapter.py
"""

from typing import TYPE_CHECKING

from integrations.base.interface import AdapterInterface
from integrations.discord.api import AdapterAPI
from integrations.discord.config import SvcConfig
from integrations.discord.functions import SvcFunctions
from integrations.discord.parser import MessageParser
from libs.types import ServiceType

if TYPE_CHECKING:
    from configparser import ConfigParser


class ServiceAdapter(AdapterInterface[SvcConfig, AdapterAPI, SvcFunctions, MessageParser]):
    """discord interface"""

    interface_type = ServiceType.DISCORD

    def __init__(self, parser: "ConfigParser") -> None:
        """
        Discord連携用アダプタを初期化する。

        Args:
            parser (ConfigParser): アプリケーション設定を保持する設定パーサー。

        """
        self.conf = SvcConfig(main_conf=parser)
        self.api = AdapterAPI()
        self.functions = SvcFunctions(api=self.api, conf=self.conf)
        self.parser = MessageParser
