"""
libs/commands/registry/member.py
"""

import logging
from typing import TYPE_CHECKING, TypedDict

import libs.global_value as g
from libs.bootstrap.app_config import BaseSection
from libs.data import lookup, modify
from libs.utils import dbutil, textutil, validator

if TYPE_CHECKING:
    from libs.bootstrap.app_config import AppConfig


class MemberDataDict(TypedDict):
    """メンバー情報格納辞書"""

    id: int
    """メンバーID"""

    name: str
    """メンバー名"""

    alias: list[str]
    """別名リスト"""


class MemberSection(BaseSection):
    """memberセクション処理"""

    section: str
    info: list[MemberDataDict]
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
        self.section = "member"
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


def append(argument: list) -> str:
    """メンバー追加

    Args:
        argument (list): 登録情報
            - argument[0]: 登録するメンバー名
            - argument[1]: 登録する別名

    Returns:
        str: 処理結果
    """

    resultdb = dbutil.connection(g.cfg.setting.database_file)

    ret: bool = False
    dbupdate_flg: bool = False
    msg: str = "使い方が間違っています。"

    if len(argument) == 1:  # 新規追加
        new_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        rows = resultdb.execute("select count() from member")
        count = rows.fetchone()[0]
        if count > g.cfg.member.registration_limit:
            msg = "登録上限を超えています。"
        else:  # 登録処理
            ret, msg = validator.check_namepattern(new_name, "member")
            if ret:
                resultdb.execute(
                    "insert into member(name) values (?)",
                    (new_name,),
                )
                resultdb.execute(
                    "insert into alias(name, member) values (?,?)",
                    (new_name, new_name),
                )
                msg = f"「{new_name}」を登録しました。"
                logging.info("add new member: %s", new_name)

    if len(argument) == 2:  # 別名登録
        new_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        nic_name = textutil.str_conv(argument[1], textutil.ConversionType.HtoZ)
        registration_flg = True
        rows = resultdb.execute(
            "select count() from alias where member=?",
            (new_name,),
        )
        count = rows.fetchone()[0]
        if count == 0:
            msg = f"「{new_name}」はまだ登録されていません。"
            registration_flg = False
        if count > g.cfg.member.alias_limit:
            msg = "登録上限を超えています。"
            registration_flg = False

        if registration_flg:  # 登録処理
            ret, msg = validator.check_namepattern(nic_name, "member")
            if ret:
                resultdb.execute(
                    "insert into alias(name, member) values (?,?)",
                    (nic_name, new_name),
                )
                msg = f"「{new_name}」に「{nic_name}」を追加しました。"
                logging.info("add alias: %s -> %s", new_name, nic_name)
                dbupdate_flg = True

        if dbupdate_flg:
            rows = resultdb.execute(
                """
                select distinct name from (
                    select p1_name as name from result
                    union all select p2_name from result
                    union all select p3_name from result
                    union all select p4_name from result
                    union all select name from remarks
                );
                """
            )
            name_list = [row["name"] for row in rows.fetchall()]

            if {
                nic_name,
                textutil.str_conv(nic_name, textutil.ConversionType.KtoH),
                textutil.str_conv(nic_name, textutil.ConversionType.HtoK),
            } & set(name_list):
                msg += modify.db_backup()
                for tbl, col in [("result", f"p{x}_name") for x in range(1, 5)] + [("remarks", "name")]:
                    resultdb.execute(
                        f"update {tbl} set {col}=? where {col}=?",
                        (new_name, nic_name),
                    )
                    resultdb.execute(
                        f"update {tbl} set {col}=? where {col}=?",
                        (new_name, textutil.str_conv(nic_name, textutil.ConversionType.KtoH)),
                    )
                    resultdb.execute(
                        f"update {tbl} set {col}=? where {col}=?",
                        (new_name, textutil.str_conv(nic_name, textutil.ConversionType.HtoK)),
                    )
                msg += "\nデータベースを更新しました。"

    resultdb.commit()
    resultdb.close()

    g.cfg.member.info = lookup.get_member_info()
    return msg


def remove(argument: list) -> str:
    """メンバー削除

    Args:
        argument (list): 削除情報
            - argument[0]: 削除するメンバー名
            - argument[1]: 削除する別名

    Returns:
        str: 処理結果
    """

    resultdb = dbutil.connection(g.cfg.setting.database_file)
    msg = "使い方が間違っています。"

    if len(argument) == 1:  # メンバー削除
        new_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        if new_name in g.cfg.member.lists:
            resultdb.execute(
                "delete from member where name=?",
                (new_name,),
            )
            resultdb.execute(
                "delete from alias where member=?",
                (new_name,),
            )
            msg = f"「{new_name}」を削除しました。"
            logging.info("remove member: %s", new_name)
        else:
            msg = f"「{new_name}」は登録されていません。"

    if len(argument) == 2:  # 別名削除
        new_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        nic_name = textutil.str_conv(argument[1], textutil.ConversionType.HtoZ)
        if nic_name in g.cfg.member.lists:
            resultdb.execute(
                "delete from alias where name=? and member=?",
                (nic_name, new_name),
            )
            msg = f"「{new_name}」から「{nic_name}」を削除しました。"
            logging.info("alias remove: %s -> %s", new_name, nic_name)
        else:
            msg = f"「{new_name}」に「{nic_name}」は登録されていません。"

    resultdb.commit()
    resultdb.close()

    g.cfg.member.info = lookup.get_member_info()
    return msg
