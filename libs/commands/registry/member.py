"""
libs/commands/registry/member.py
"""

import logging
from typing import TYPE_CHECKING, TypedDict, cast

import libs.global_value as g
from libs.domain import modify
from libs.domain.datamodels import SettingAttrs
from libs.domain.section import BaseSection
from libs.functions import validator
from libs.functions.compose import text_item
from libs.types import CommandType, StyleOptions
from libs.utils import dbutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class MemberDataDict(TypedDict):
    """メンバー情報格納辞書"""

    id: int
    """メンバーID"""
    name: str
    """メンバー名"""
    alias: list[str]
    """別名リスト"""
    team: str
    """所属チーム"""
    last_update: int
    """最終更新日"""
    elapsed_day: int
    """経過日数"""
    game_count: int
    """対戦数"""


class MemberConfig(BaseSection, SettingAttrs):
    """memberセクション処理"""

    info: list[MemberDataDict]
    """メンバー情報(キャッシュデータ)"""
    registration_limit: int
    """登録メンバー上限数"""
    character_limit: int
    """名前に使用できる文字数"""
    alias_limit: int
    """別名登録上限数"""
    guest_name: str
    """未登録メンバー名称"""

    def __init__(self) -> None:
        """
        MemberConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。
        """
        self.command_name: str = "メンバー一覧"
        self.default_commandword: str = "メンバー一覧"
        self.section: str = "member"
        self.default_reset()

    def register(self) -> None:
        """
        ディスパッチャー登録。

        メンバー一覧の呼び出しワードをディスパッチャーテーブルに登録する。

        """
        for commandword in self.commandwords_list():
            g.keyword_dispatcher.update({commandword: members_list})

    def default_reset(self) -> None:
        """デフォルト値にリセット"""
        self.info = []
        self.commandword = []
        self.command_suffix = []
        self.registration_limit = int(255)
        self.character_limit = int(8)
        self.alias_limit = int(16)
        self.guest_name = str("ゲスト")

    def resolve_name(self, name: str) -> str:
        """
        別名からメンバー名を逆引き

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
        """
        指定メンバーの別名をリストで返す

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
        """
        メンバー名、別名をすべてリストで返す

        Returns:
            list[str]: メンバー名、別名のリスト

        """
        ret: list[str] = []
        for name in self.lists:
            ret.append(name)
            ret.extend(self.alias(name))

        return list(set(ret))

    @property
    def get_info(self) -> list[MemberDataDict]:
        """
        全メンバー情報取得

        Returns:
            list[MemberDataDict]: メンバー情報

        """
        ret = g.params.read_data("MEMBER_INFO").to_dict(orient="records")
        for row in ret:
            row.update(alias=str(row["alias"]).split(","))

        return cast(list[MemberDataDict], ret)


def members_list(m: "MessageParserProtocol") -> None:
    """
    メンバーの登録一覧を返す

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    """
    m.status.command_type = CommandType.MEMBERS_LIST
    m.set_message(text_item.get_members_list(), StyleOptions(title="登録済みメンバー", codeblock=True))
    m.post.ts = m.data.event_ts
    m.post.thread_title = "登録済みメンバー"


def append(argument: list[str]) -> str:
    """
    メンバー追加

    Args:
        argument (list[str]): 登録情報

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

    g.cfg.member.info = g.cfg.member.get_info

    return msg


def remove(argument: list[str]) -> str:
    """
    メンバー削除

    Args:
        argument (list[str]): 削除情報

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

    g.cfg.member.info = g.cfg.member.get_info

    return msg
