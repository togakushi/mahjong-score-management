"""
libs/commands/registry/configuration.py
"""

import logging
from typing import TYPE_CHECKING

from libs.bootstrap.app_config import BaseSection

if TYPE_CHECKING:
    from libs.bootstrap.app_config import AppConfig
    from libs.types import MemberDataDict, TeamDataDict


class MemberSection(BaseSection):
    """memberセクション処理"""

    info: list["MemberDataDict"]
    """メンバー情報"""
    registration_limit: int
    """登録メンバー上限数"""
    character_limit: int
    """名前に使用できる文字数"""
    alias_limit: int
    """別名登録上限数"""
    guest_name: str
    """未登録メンバー名称"""

    def __init__(self):
        self._reset()

    def _reset(self):
        self.info = []
        self.registration_limit = int(255)
        self.character_limit = int(8)
        self.alias_limit = int(16)
        self.guest_name = str("ゲスト")

    def config_load(self, outer: "AppConfig"):
        """設定値取り込み

        Args:
            outer (AppConfig): 設定クラスオブジェクト
        """

        self.section: str = "member"
        self._parser = outer._parser
        self._reset()
        super().__init__(
            self,
        )

        # 呼び出しキーワード取り込み
        self.commandword = [x.strip() for x in self._parser.get(self.section, "commandword", fallback="メンバー一覧").split(",")]

        logging.debug("%s: %s", self.section, self)

    def resolve_name(self, name: str) -> str:
        """別名からメンバー名を逆引き

        Args:
            name (str): 変換する名前

        Returns:
            str: メンバー名(見つからない場合は空欄)
        """

        for x in self.info:
            if name in x["alias"]:
                return x["name"]

        return ""

    def alias(self, name: str) -> list[str]:
        """指定メンバーの別名をリストで返す

        Args:
            name (str): メンバー名

        Returns:
            list[str]: 別名リスト
        """

        for x in self.info:
            if x.get("name") == name:
                return x.get("alias")
        return []

    @property
    def lists(self) -> list[str]:
        """メンバー名一覧をリストで返す"""

        return [x.get("name") for x in self.info]

    @property
    def all_lists(self) -> list[str]:
        """メンバー名、別名をすべてリストで返す

        Returns:
            list[str]: メンバー名、別名のリスト
        """

        ret: list[str] = []
        for name in self.lists:
            ret.append(name)
            ret.extend(self.alias(name))

        return list(set(ret))


class TeamSection(BaseSection):
    """teamセクション処理"""

    info: list["TeamDataDict"]
    """チーム情報"""
    registration_limit: int
    """登録チーム上限数"""
    character_limit: int
    """チーム名に使用できる文字数"""
    member_limit: int
    """チームに所属できるメンバー上限"""
    friendly_fire: bool
    """チームメイトが同卓しているゲームを集計対象に含めるか"""

    def __init__(self):
        self._reset()

    def _reset(self):
        self.info = []
        self.registration_limit = int(255)
        self.character_limit = int(16)
        self.member_limit = int(16)
        self.friendly_fire = bool(True)

    def config_load(self, outer: "AppConfig"):
        """設定値取り込み

        Args:
            outer (AppConfig): 設定クラスオブジェクト
        """

        self.section: str = "team"
        self._parser = outer._parser
        self._reset()
        super().__init__(self)

        # 呼び出しキーワード取り込み
        self.commandword = [x.strip() for x in self._parser.get(self.section, "commandword", fallback="チーム一覧").split(",")]

        logging.debug("%s: %s", self.section, self)

    def member(self, team: str) -> list[str]:
        """チーム所属メンバーをリストで返す

        Args:
            team (str): チーム名

        Returns:
            list[str]: 所属メンバーリスト
        """

        for x in self.info:
            if x.get("team") == team:
                return x.get("member")
        return []

    def which(self, name: str) -> str | None:
        """指定メンバーの所属チームを返す

        Args:
            name (str): チェック対象のメンバー名

        Returns:
            Union[str, None]:
            - str: 所属しているチーム名
            - None: 未所属
        """

        for team in self.lists:
            if name in self.member(team):
                return team

        return None

    @property
    def lists(self) -> list[str]:
        """チーム名一覧をリストで返す

        Returns:
            list[str]: チーム名一覧
        """

        return [x.get("team") for x in self.info]
