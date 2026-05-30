"""
integrations/web/adapter.py
"""

from typing import TYPE_CHECKING

from integrations.base.interface import AdapterInterface
from integrations.web.api import AdapterAPI
from integrations.web.config import SvcConfig
from integrations.web.functions import SvcFunctions
from integrations.web.parser import MessageParser
from libs.types import ServiceType

if TYPE_CHECKING:
    from configparser import ConfigParser


class ServiceAdapter(AdapterInterface[SvcConfig, AdapterAPI, SvcFunctions, MessageParser]):
    """web interface"""

    interface_type = ServiceType.WEB

    def __init__(self, parser: "ConfigParser") -> None:
        """
        Web連携用アダプタを初期化する。

        Args:
            parser (ConfigParser): アプリケーション設定を保持する設定パーサー。

        """
        self.conf = SvcConfig(main_conf=parser)
        self.api = AdapterAPI()
        self.functions = SvcFunctions()
        self.parser = MessageParser
