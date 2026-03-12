"""
integrations/web/api.py
"""

from typing import TYPE_CHECKING

from integrations.base.interface import APIInterface

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class AdapterAPI(APIInterface):
    """ダミークラス"""

    def post(self, m: "MessageParserProtocol") -> None:
        """Abstractmethod dummy"""
        _ = m
