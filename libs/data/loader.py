"""
libs/data/loader.py
"""

import logging
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Any, Optional

import pandas as pd

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


def read_data(keyword: str, params: Optional[dict[str, Any]] = None) -> pd.DataFrame:
    """
    データベースからデータを取得する

    Args:
        keyword (str): SQL選択キーワード
        params (Optional[dict[str, Any]]): プレースホルダ

    Returns:
        pd.DataFrame: 集計結果

    """
    if not params:
        params = g.params.placeholder()

    g.params.update_from_dict(params)
    sql = g.params.query_modification(dbutil.query(keyword))

    if g.args.verbose & 0x01:
        print(f">>> params={g.params.placeholder()}")
        print(f">>> SQL: {keyword} -> {g.cfg.setting.database_file}\n{g.params.named_query(sql)}")

    try:
        query_start_time = datetime.now().timestamp()
        df = pd.read_sql(
            sql=sql,
            con=dbutil.connection(g.cfg.setting.database_file),
            params=params,
        )
        query_end_time = datetime.now().timestamp()
    except pd.errors.DatabaseError as err:
        logging.error("DatabaseError: %s", err)
        logging.error("SQL: %s, DATABASE: %s", keyword, g.cfg.setting.database_file)
        logging.error("params=%s", g.params.placeholder())
        logging.error("query: %s", g.params.named_query(sql))

    if g.args.verbose & 0x02:
        print("=" * 80)
        print(df.to_string())

    logging.debug("SQL: %s, time: %s", keyword, query_end_time - query_start_time)
    return df
