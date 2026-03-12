"""
integrations/standard_io/functions.py
"""

from typing import TYPE_CHECKING, Any

from integrations.base.interface import FunctionsInterface
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class SvcFunctions(FunctionsInterface):
    """標準入出力専用関数"""

    def post_processing(self, m: "MessageParserProtocol") -> None:
        """
        後処理

        Args:
            m (MessageParserProtocol): メッセージデータ

        """
        print(ExtDt(float(m.data.event_ts)), m.status.message)

    def get_conversations(self, m: "MessageParserProtocol") -> dict[str, Any]:
        """Abstractmethod dummy"""
        _ = m
        return {}
