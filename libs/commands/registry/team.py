"""
libs/registry/team.py
"""

import logging
from typing import TYPE_CHECKING, TypedDict, cast

import libs.global_value as g
from libs.bootstrap import initialization
from libs.domain import modify
from libs.domain.datamodels import SettingAttrs
from libs.domain.section import BaseSection
from libs.functions import validator
from libs.functions.compose import text_item
from libs.types import StyleOptions
from libs.utils import dbutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class TeamDataDict(TypedDict):
    """チーム情報格納辞書"""

    id: int
    """チームID"""
    team: str
    """チーム名"""
    members: list[str]
    """所属メンバーリスト"""


class TeamConfig(BaseSection, SettingAttrs):
    """teamセクション処理"""

    info: list[TeamDataDict]
    """チーム情報(キャッシュデータ)"""
    registration_limit: int
    """登録チーム上限数"""
    character_limit: int
    """チーム名に使用できる文字数"""
    member_limit: int
    """チームに所属できるメンバー上限"""
    friendly_fire: bool
    """チームメイトが同卓しているゲームを集計対象に含めるか"""

    def __init__(self) -> None:
        """
        TeamConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。
        """
        self.command_name: str = "チーム一覧"
        self.default_commandword: str = "チーム一覧"
        self.section: str = "team"
        self.default_reset()

    def register(self) -> None:
        """
        ディスパッチャー登録。

        チーム一覧の呼び出しワードをディスパッチャーテーブルに登録する。

        """
        for commandword in self.commandwords_list():
            g.keyword_dispatcher.update({commandword: team_list})

    def default_reset(self) -> None:
        """デフォルト値にリセット"""
        self.info = []
        self.commandword = []
        self.command_suffix = []
        self.registration_limit = int(255)
        self.character_limit = int(16)
        self.member_limit = int(16)
        self.friendly_fire = bool(True)

    def member(self, team: str) -> list[str]:
        """
        指定チームの所属メンバーをリストで返す

        Args:
            team (str): 対象チーム名

        Returns:
            list[str]: 所属メンバーリスト

        """
        for x in self.info:
            if x.get("team") == team:
                return x.get("members")
        return []

    def which(self, name: str) -> str | None:
        """
        指定メンバーの所属チームを返す

        Args:
            name (str): 対象メンバー名

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
        """
        チーム名一覧をリストで返す

        Returns:
            list[str]: チーム名一覧

        """
        return [x.get("team") for x in self.info]

    @property
    def get_info(self) -> list[TeamDataDict]:
        """
        全チーム情報取得

        Returns:
            list[TeamDataDict]: チーム情報

        """
        ret = g.params.read_data("TEAM_INFO").to_dict(orient="records")
        for row in ret:
            row.update(members=str(row["members"]).split(","))

        return cast(list[TeamDataDict], ret)


def team_list(m: "MessageParserProtocol") -> None:
    """
    チームの登録一覧を返す

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。
    """
    m.set_message(text_item.get_team_list(), StyleOptions(title="登録済みチーム", codeblock=True))
    m.post.ts = m.data.event_ts
    m.post.thread_title = "登録済みチーム"


def create(argument: list[str]) -> str:
    """
    チーム作成

    Args:
        argument (list[str]): 作成するチーム名

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
                g.cfg.team.info = g.cfg.team.get_info
                msg = f"チーム「{team_name}」を登録しました。"
                logging.info("add new team: %s", team_name)

    return msg


def delete(argument: list[str]) -> str:
    """
    チーム削除

    Args:
        argument (list[str]): 削除するチーム名

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
            g.cfg.team.info = g.cfg.team.get_info
            msg += f"\nチーム「{team_name}」を削除しました。"
            logging.info("team delete: %s", team_name)

    return msg


def append(argument: list[str]) -> str:
    """
    チーム所属

    Args:
        argument (list[str]): 登録情報

            - argument[0]: 所属させるチーム名
            - argument[1]: 所属するメンバー名

    Returns:
        str: 処理結果

    """
    msg = "使い方が間違っています。"

    if len(argument) == 1:  # 新規作成
        msg = create(argument)

    if len(argument) == 2:  # チーム所属
        g.params.unregistered_replace = False

        team_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        player_name = textutil.name_replace(argument[1])
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
            g.cfg.team.info = g.cfg.team.get_info
            msg = f"チーム「{team_name}」に「{player_name}」を所属させました。"
            logging.info("team participation: %s -> %s", team_name, player_name)

    return msg


def remove(argument: list[str]) -> str:
    """
    チームから除名

    Args:
        argument (list[str]): 登録情報

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
        g.params.unregistered_replace = False
        team_name = textutil.str_conv(argument[0], textutil.ConversionType.HtoZ)
        player_name = textutil.name_replace(argument[1])

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
            g.cfg.team.info = g.cfg.team.get_info
            msg = f"チーム「{team_name}」から「{player_name}」を離脱させました。"
            logging.info("team breakaway: %s -> %s", team_name, player_name)

    return msg


def clear() -> str:
    """
    全チーム削除

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
    g.cfg.member.info = g.cfg.member.get_info
    g.cfg.team.info = g.cfg.team.get_info

    return msg
