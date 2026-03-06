"""
libs/commands/ranking/configuration.py
"""

import logging
from typing import TYPE_CHECKING

from libs.bootstrap.app_config import BaseSection
from libs.domain.datamodels import CommandAttrs

if TYPE_CHECKING:
    from libs.bootstrap.app_config import AppConfig


class RankingConfig(BaseSection, CommandAttrs):
    """サブコマンドセクション処理"""

    def __init__(self):
        self.default_reset("ranking")

    def config_load(self, outer: "AppConfig"):
        """設定値取り込み

        Args:
            outer (AppConfig): 設定クラスオブジェクト
        """

        self._parser = outer._parser
        self._section = outer._parser[self.section]
        self.default_reset(self.section)
        super().__init__(self, self.section)

        # 呼び出しキーワード取り込み
        self.commandword = self.getlist("commandword", "麻雀ランキング")

        logging.debug("%s: %s", self.section, self)
