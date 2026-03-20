"""
libs/data/loader.py
"""

import logging
import sqlite3
from contextlib import closing
from typing import Any, Optional

import libs.global_value as g
from libs.utils import dbutil


def execute(query: str, params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    """
    クエリ実行

    Args:
        query (str): 実行クエリ
        params (Optional[dict[str,Any]]): プレースホルダ

    Returns:
        list[dict[str, Any]]: 実行結果

    """
    if not params:
        params = g.params.placeholder()

    ret: list[dict[str, Any]] = []

    g.params.update_from_dict(params)
    query = g.params.query_modification(query)

    if g.args.verbose & 0x01:
        print(f">>> params={g.params.placeholder()}")
        print(f">>> SQL -> {g.cfg.setting.database_file}\n{g.params.named_query(query)}")

    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        try:
            rows = conn.execute(query, params)
            if conn.total_changes:
                conn.commit()
        except sqlite3.OperationalError as err:
            logging.error("OperationalError: %s", err)
            logging.error("params=%s", g.params.placeholder())
            logging.error("query: %s", g.params.named_query(query))
            return ret

        for row in rows.fetchall():
            ret.append(dict(row))

        if g.args.verbose & 0x02:
            print("=" * 80)
            print(ret)

    return ret
