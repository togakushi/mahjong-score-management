"""
libs/data/search.py
"""

import logging
from contextlib import closing
from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain.score import GameResult
from libs.utils import dbutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from libs.types import RemarkDict


def for_db_score(first_ts: float) -> list[GameResult]:
    """
    データベースからスコアを検索して返す

    Args:
        first_ts (float): 検索を開始する時刻

    Returns:
        list[GameResult]: 検索した結果

    """
    data: list[GameResult] = []
    rows = dbutil.execute(
        "select * from result where ts >= :first_ts and source like :source",
        {"first_ts": str(first_ts), "source": f"{g.adapter.interface_type}_%"},
    )

    for row in rows:
        data.append(GameResult(**row))

    logging.debug(data)
    return data


def for_db_remarks(first_ts: float) -> list["RemarkDict"]:
    """
    データベースからメモを検索して返す

    Args:
        first_ts (float): 検索を開始する時刻

    Returns:
        list[RemarkDict]: 検索した結果

    """
    data: list["RemarkDict"] = []
    with closing(dbutil.connection(g.cfg.setting.database_file)) as cur:
        # 記録済みメモ内容
        rows = cur.execute(
            dbutil.query("REMARKS_SELECT"),
            (str(first_ts), f"{g.adapter.interface_type}_%"),
        )
        for row in rows.fetchall():
            data.append(
                {
                    "thread_ts": row["thread_ts"],
                    "event_ts": row["event_ts"],
                    "name": row["name"],
                    "matter": row["matter"],
                    "source": row["source"],
                }
            )
    logging.debug(data)
    return data


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
