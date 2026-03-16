"""
libs/data/lookup.py
"""

import logging
from configparser import ConfigParser
from contextlib import closing
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union, cast

import libs.global_value as g
from libs.data import loader
from libs.domain.datamodels import ChannelType, CommandType
from libs.domain.score import GameResult
from libs.utils import dbutil
from libs.utils.timekit import ExtendedDatetime as ExtDt
from libs.utils.timekit import Format

if TYPE_CHECKING:
    from pathlib import Path

    from integrations.protocols import MessageParserProtocol


def get_config_value(
    config_file: "Path",
    section: str,
    name: str,
    val_type: type,
    fallback: Union[bool, int, float, str, list[Any], None] = None,
) -> Any:
    """
    設定値取得

    Args:
        config_file (Path): 設定ファイルパス
        section (str): セクション名
        name (str): 項目名
        val_type (type): 取り込む値の型 (bool, int, float, str, list[Any])
        fallback (Union[bool, int, float, str, list[Any]], optional): 項目が見つからない場合に返す値. Defaults to None

    Returns:
        Any: 取得した値
            - 実際に返す型: Union[int, float, bool, str, list[Any], None]

    Raises:
        TypeError: val_type が bool, int, float, str, list 以外の場合

    """
    value: Union[int, float, bool, str, list[Any], None] = fallback
    parser = ConfigParser()
    parser.read(config_file, encoding="utf-8")

    if parser.has_option(section, name):
        match val_type:
            case x if x is int:
                value = parser.getint(section, name)
            case x if x is float:
                value = parser.getfloat(section, name)
            case x if x is bool:
                value = parser.getboolean(section, name)
            case x if x is str:
                value = parser.get(section, name)
            case x if x is list:
                value = [x.strip() for x in parser.get(section, name).split(",")]
            case _:
                raise TypeError(f"Unsupported val_type: {val_type}")

    return value


def resolve_separate_flag(m: "MessageParserProtocol") -> bool:
    """
    優先度の高いセパレート設定フラグを取得する

    Args:
        m (MessageParserProtocol): メッセージデータ

    Returns:
        bool: セパレート設定フラグ

    """
    separate_flg: Optional[bool] = None

    # DM / HomeApp(slack) はセパレートしない
    if m.data.channel_type in {ChannelType.DIRECT_MESSAGE, ChannelType.HOME_APP}:
        return False

    if g.cfg.main_parser.has_section(m.status.source):
        # チャンネル個別ファイル内設定
        if channel_config := g.cfg.main_parser[m.status.source].get("channel_config"):
            separate_flg = get_config_value(config_file=Path(channel_config), section="setting", name="separate", val_type=bool)
            if separate_flg is not None:
                return separate_flg
        # チャンネル設定
        else:
            separate_flg = get_config_value(config_file=g.cfg.config_file, section=m.status.source, name="separate", val_type=bool)
            if separate_flg is not None:
                return separate_flg

    # サービス別設定
    separate_flg = get_config_value(config_file=g.cfg.config_file, section=g.adapter.interface_type, name="separate", val_type=bool)
    if separate_flg is not None:
        return separate_flg

    # メイン設定
    separate_flg = get_config_value(config_file=g.cfg.config_file, section="setting", name="separate", val_type=bool)
    if separate_flg is not None:
        return separate_flg

    return False


def member_info(params: dict[str, Any]) -> dict[str, Any]:
    """
    指定メンバーの記録情報を返す

    Args:
        params (dict[str, Any]): 対象メンバー

    Returns:
        dict[str, Any]: 記録情報

    """
    params.update({"starttime": cast(ExtDt, params["starttime"]).format(Format.SQL)})
    params.update({"endtime": cast(ExtDt, params["endtime"]).format(Format.SQL)})
    ret = loader.execute(
        """
        select
            count() as game_count,
            min(ts) as first_game,
            max(ts) as last_game,
            max(rpoint) as rpoint_max,
            min(rpoint) as rpoint_min
        from
            individual_results
        where
            mode = :mode
            and rule_version in (<<rule_list>>)
            and playtime between :starttime and :endtime
            --[separate] and source = :source
            --[individual] and name = :player_name
            --[team] and team = :player_name
        ;
        """,
        params,
    )

    return ret[0]


def get_guest() -> str:
    """
    ゲスト名取得

    Returns:
        str: ゲスト名

    """
    guest_name: str = ""
    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        rows = conn.execute("select name from member where id=0")
        guest_name = str(rows.fetchone()[0])

    return guest_name


def regulation_list(word_type: int = 0, rule_version: str | None = None) -> list[str]:
    """
    登録済みワードリストを取得する

    Args:
        word_type (int, optional): 取得するタイプ. Defaults to 0.
        rule_version (str, optional): ルール識別子

    Returns:
        list[str]: 取得結果

    """
    ret: list[str] = []

    if not rule_version and not (rule_version := g.params.default_rule):
        return []

    with closing(dbutil.connection(g.cfg.setting.database_file)) as cur:
        rows = cur.execute(
            """
            select
                word,
                ex_point
            from
                words
            where
                type=?
                and rule_version=?
            """,
            (word_type, rule_version),
        ).fetchall()

    for word, ex_point in rows:
        if ex_point:
            point = f"{ex_point:.1f}".replace("-", "▲")
            ret.append(f"{word}\t{point}pt")
        else:
            ret.append(f"{word}")

    return ret


def resolve_commands(rule_version: str, command_type: CommandType) -> list[str]:
    """
    ルール識別子で割り当てられているコマンドワードを返す

    Args:
        rule_version (str): ルール識別子
        command_type (CommandType): コマンド種別

    Returns:
        list[str]: コマンドワード

    """
    keywords: list[str] = [word for word, rule in g.cfg.rule.keyword_mapping.items() if rule == rule_version]
    commandwords: list[str] = []

    match command_type:
        case CommandType.RESULTS:
            commandwords.append(g.cfg.results.default_commandword)
            commandwords.extend(g.cfg.results.commandword)
            commandwords.extend([f"{command}{suffix}" for suffix in g.cfg.results.command_suffix for command in keywords])
        case CommandType.GRAPH:
            commandwords.append(g.cfg.graph.default_commandword)
            commandwords.extend(g.cfg.graph.commandword)
            commandwords.extend([f"{command}{suffix}" for suffix in g.cfg.graph.command_suffix for command in keywords])
        case CommandType.RANKING:
            commandwords.append(g.cfg.ranking.default_commandword)
            commandwords.extend(g.cfg.ranking.commandword)
            commandwords.extend([f"{command}{suffix}" for suffix in g.cfg.ranking.command_suffix for command in keywords])
        case CommandType.REPORT:
            commandwords.append(g.cfg.report.default_commandword)
            commandwords.extend(g.cfg.report.commandword)
            commandwords.extend([f"{command}{suffix}" for suffix in g.cfg.report.command_suffix for command in keywords])
        case CommandType.MEMBER_LIST:
            commandwords.append(g.cfg.member.default_commandword)
            commandwords.extend(g.cfg.member.commandword)
            commandwords.extend([f"{command}{suffix}" for suffix in g.cfg.member.command_suffix for command in keywords])
        case CommandType.TEAM_LIST:
            commandwords.append(g.cfg.team.default_commandword)
            commandwords.extend(g.cfg.team.commandword)
            commandwords.extend([f"{command}{suffix}" for suffix in g.cfg.team.command_suffix for command in keywords])
        case CommandType.HELP:
            commandwords.append(g.cfg.help.default_commandword)
            commandwords.extend(g.cfg.help.commandword)
            commandwords.extend([f"{command}{suffix}" for suffix in g.cfg.help.command_suffix for command in keywords])
        case _:
            return []

    return [x for x in g.keyword_dispatcher if x in commandwords]


def exsist_record(ts: str) -> GameResult:
    """
    記録されているゲーム結果を返す

    Args:
        ts (str): 検索するタイムスタンプ

    Returns:
        GameResult: スコアデータ

    """
    result = GameResult()

    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        row = conn.execute(
            """
            select
                ts,
                p1_name, p1_str,
                p2_name, p2_str,
                p3_name, p3_str,
                p4_name, p4_str,
                comment,
                rule_version
            from
                result where ts = :ts
            ;
            """,
            {"ts": ts},
        ).fetchone()

    if row:
        result.calc(**dict(row))

    return result


def first_record(rule_list: list[str]) -> ExtDt:
    """
    最初のゲーム記録時間を返す

    Args:
        rule_list (list[str]): ルール識別子

    Returns:
        ExtendedDatetime: 最初のゲーム記録時間

    """
    ret = ExtDt()
    rule_dict = {f"rule_{idx}": name for idx, name in enumerate(set(rule_list))}

    try:
        with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
            table_count = conn.execute(
                "select count() from sqlite_master where type='view' and name='game_results';",
            ).fetchall()[0][0]

            if table_count:
                sql = "select min(playtime) from game_results where rule_version in (<<rule_list>>);".replace("<<rule_list>>", ":" + ", :".join(rule_dict))
                record = conn.execute(sql, rule_dict).fetchall()[0][0]
                if record:
                    ret = ExtDt(str(record)) - {"hour": 0, "minute": 0, "second": 0, "microsecond": 0, "hours": g.cfg.setting.time_adjust}
    except AttributeError:
        ret = ExtDt()

    return ret


def read_memberslist() -> None:
    """メンバー情報/チーム情報の読み込み"""
    g.cfg.member.guest_name = get_guest()
    g.cfg.member.info = g.cfg.member.get_info
    g.cfg.team.info = g.cfg.team.get_info

    logging.debug("guest_name: %s", g.cfg.member.guest_name)
    logging.debug("member_list: %s", g.cfg.member.lists)
    logging.debug("team_list: %s", g.cfg.team.lists)


def enumeration_all_members() -> list[str]:
    """
    メンバーとチームをすべて列挙する

    Returns:
        list[str]: メンバー名(別名含む)/チーム名のリスト

    """
    ret_list: list[str] = []

    for member in g.cfg.member.info:
        ret_list.append(member.get("name"))
        ret_list.extend(member.get("alias"))
    ret_list.extend([team.get("team") for team in g.cfg.team.info])

    return list(set(ret_list))
