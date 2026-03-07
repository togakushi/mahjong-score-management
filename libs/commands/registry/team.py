"""
libs/registry/team.py
"""

import logging
from typing import TYPE_CHECKING, TypedDict

import libs.global_value as g
from libs.bootstrap.app_config import BaseSection
from libs.data import initialization, lookup, modify
from libs.utils import dbutil, formatter, textutil, validator

if TYPE_CHECKING:
    from libs.bootstrap.app_config import AppConfig


class TeamDataDict(TypedDict):
    """チーム情報格納辞書"""

    id: int
    """チームID"""
    team: str
    """チーム名"""
    member: list[str]
    """所属メンバーリスト"""


class TeamSection(BaseSection):
    """teamセクション処理"""

    section: str
    info: list[TeamDataDict]
    """チーム情報"""
    registration_limit: int
    """登録チーム上限数"""
    character_limit: int
    """チーム名に使用できる文字数"""
    member_limit: int
    """チームに所属できるメンバー上限"""
    friendly_fire: bool
    """チームメイトが同卓しているゲームを集計対象に含めるか"""

    def __init__(self, outer: "AppConfig"):
        self.section = "team"
        self.main_parser = outer.main_parser
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

        self._reset()
        super().__init__(self)

        # 呼び出しキーワード取り込み
        self.commandword = self.getlist("commandword", fallback="チーム一覧")

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


def create(argument: list) -> str:
    """チーム作成

    Args:
        argument (list): 作成するチーム名

    Returns:
        str: 処理結果
    """

    ret = False
    msg = "使い方が間違っています。"

    if len(argument) == 1:  # 新規追加
        team_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        if len(g.cfg.team.lists) > g.cfg.team.registration_limit:
            msg = "登録上限を超えています。"
        else:  # 登録処理
            ret, msg = validator.check_namepattern(team_name, "team")
            if ret:
                resultdb = dbutil.connection(g.cfg.setting.database_file)
                resultdb.execute(
                    "insert into team(name) values (?)",
                    (team_name,),
                )
                resultdb.commit()
                resultdb.close()
                g.cfg.team.info = lookup.get_team_info()
                msg = f"チーム「{team_name}」を登録しました。"
                logging.info("add new team: %s", team_name)

    return msg


def delete(argument: list) -> str:
    """チーム削除

    Args:
        argument (list): 削除するチーム名

    Returns:
        str: 処理結果
    """

    msg = "使い方が間違っています。"

    if len(argument) == 1:  # 新規追加
        team_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        if team_name not in g.cfg.team.lists:  # 未登録チームチェック
            msg = f"チーム「{team_name}」は登録されていません。"
        else:
            msg = modify.db_backup()
            team_id = [x["id"] for x in g.cfg.team.info if x["team"] == team_name][0]
            resultdb = dbutil.connection(g.cfg.setting.database_file)
            resultdb.execute("delete from team where id = ?", (team_id,))
            resultdb.execute(
                "update member set team_id = null where team_id = ?",
                (team_id,),
            )
            resultdb.commit()
            resultdb.close()
            g.cfg.team.info = lookup.get_team_info()
            msg += f"\nチーム「{team_name}」を削除しました。"
            logging.info("team delete: %s", team_name)

    return msg


def append(argument: list) -> str:
    """チーム所属

    Args:
        argument (list): 登録情報
            - argument[0]: 所属させるチーム名
            - argument[1]: 所属するメンバー名

    Returns:
        str: 処理結果
    """

    msg = "使い方が間違っています。"

    if len(argument) == 1:  # 新規作成
        msg = create(argument)

    if len(argument) == 2:  # チーム所属
        g.params.update({"unregistered_replace": False})

        team_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        player_name = formatter.name_replace(argument[1])
        registration_flg = True
        team_id = None

        if team_name not in g.cfg.team.lists:  # 未登録チームチェック
            msg = f"チーム「{team_name}」はまだ登録されていません。"
            registration_flg = False
        else:
            team_id = [x["id"] for x in g.cfg.team.info if x["team"] == team_name][0]

        if player_name not in g.cfg.member.lists:  # 未登録プレイヤーチェック
            msg = f"「{player_name}」はレギュラーメンバーではありません。"
            registration_flg = False

        # 登録上限を超えていないか？
        # select count() from member where team_id=? group by team_id;
        # rows = resultdb.execute("select count() from team where name=?", (team_name,))
        # count = rows.fetchone()[0]
        # if count > g.cfg.team.member_limit:
        #    msg = f"登録上限を超えています。"
        #    registration_flg = False

        if registration_flg and team_id:  # 登録処理
            resultdb = dbutil.connection(g.cfg.setting.database_file)
            resultdb.execute(
                "update member set team_id = ? where name = ?",
                (team_id, player_name),
            )
            resultdb.commit()
            resultdb.close()
            g.cfg.team.info = lookup.get_team_info()
            msg = f"チーム「{team_name}」に「{player_name}」を所属させました。"
            logging.info("team participation: %s -> %s", team_name, player_name)

    return msg


def remove(argument: list) -> str:
    """チームから除名

    Args:
        argument (list): 登録情報
            - argument[0]: 対象チーム名
            - argument[1]: チームから離脱するメンバー名

    Returns:
        str: 処理結果
    """

    msg = "使い方が間違っています。"

    resultdb = dbutil.connection(g.cfg.setting.database_file)

    if len(argument) == 1:
        msg = delete(argument)

    if len(argument) == 2:  # チーム名指
        g.params.update({"unregistered_replace": False})
        team_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        player_name = formatter.name_replace(argument[1])

        registration_flg = True
        team_id = None

        if team_name not in g.cfg.team.lists:  # 未登録チームチェック
            msg = f"チーム「{team_name}」は登録されていません。"
            registration_flg = False
        else:
            team_id = [x["id"] for x in g.cfg.team.info if x["team"] == team_name][0]

        if player_name not in g.cfg.member.lists:  # 未登録プレイヤーチェック
            msg = f"「{player_name}」はレギュラーメンバーではありません。"
            registration_flg = False

        if registration_flg and team_id:  # 登録処理
            resultdb = dbutil.connection(g.cfg.setting.database_file)
            resultdb.execute(
                "update member set team_id = null where name = ?",
                (player_name,),
            )
            resultdb.commit()
            resultdb.close()
            g.cfg.team.info = lookup.get_team_info()
            msg = f"チーム「{team_name}」から「{player_name}」を離脱させました。"
            logging.info("team breakaway: %s -> %s", team_name, player_name)

    return msg


def clear() -> str:
    """全チーム削除

    Returns:
        str: 処理結果
    """

    msg = modify.db_backup()

    resultdb = dbutil.connection(g.cfg.setting.database_file)
    resultdb.execute("update member set team_id = null;")
    resultdb.execute("drop table team;")
    resultdb.execute("delete from sqlite_sequence where name = 'team';")
    resultdb.commit()
    resultdb.close()

    initialization.setup_resultdb(g.cfg.setting.database_file)
    g.cfg.member.info = lookup.get_member_info()
    g.cfg.team.info = lookup.get_team_info()

    return msg
