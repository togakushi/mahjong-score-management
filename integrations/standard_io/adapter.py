"""
integrations/standard_io/adapter.py
"""

from typing import TYPE_CHECKING

from integrations.base.interface import AdapterInterface
from integrations.standard_io.api import AdapterAPI
from integrations.standard_io.config import SvcConfig
from integrations.standard_io.functions import SvcFunctions
from integrations.standard_io.parser import MessageParser
from libs.types import ServiceType

if TYPE_CHECKING:
    from configparser import ConfigParser


class ServiceAdapter(AdapterInterface[SvcConfig, AdapterAPI, SvcFunctions, MessageParser]):
    """standard input/output interface"""

    interface_type = ServiceType.STANDARD_IO

    def __init__(self, parser: "ConfigParser") -> None:
        """
        標準入出力連携用アダプタを初期化する。

        Args:
            parser (ConfigParser): アプリケーション設定を保持する設定パーサー。

        """
        self.conf = SvcConfig(main_conf=parser)
        self.api = AdapterAPI()
        self.functions = SvcFunctions()
        self.parser = MessageParser
