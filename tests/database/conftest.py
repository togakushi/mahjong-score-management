"""
database テスト共通の前処理フィクスチャを提供する。
"""

from contextlib import closing
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import pandas as pd
import pytest

import libs.global_value as g
from libs.bootstrap import configuration, initialization
from libs.bootstrap.app_config import AppConfig
from libs.functions import lookup
from libs.utils import dbutil

if TYPE_CHECKING:
    from sqlite3 import Connection


@pytest.fixture(scope="package")
def database_connection() -> Generator["Connection", Any, None]:
    """
    共有インメモリDB接続を提供する。

    パッケージ全体で同じ接続を再利用し、終了時に確実にクローズする。

    Returns:
        Generator[Connection, Any, None]: テストで共有するSQLite接続をyieldするジェネレータ。

    """
    configuration.setup(init_db=False)
    g.cfg = AppConfig(Path("tests/test_data/empty.ini"))
    g.cfg.setting.database_file = "memdb1?mode=memory&cache=shared"
    conn = dbutil.connection(g.cfg.setting.database_file)
    yield conn
    conn.close()


@pytest.fixture(scope="package", autouse=True)
def initialize_database(database_connection: Any) -> None:
    """
    テスト用DBを初期化して基礎データを投入する。

    member/team/alias テーブルを準備し、参照系テストの前提を整える。

    Args:
        database_connection (Any): 共有DB接続フィクスチャ。初期化順制御のために受け取る。

    """
    _ = database_connection  # pylint (W0613: Unused argument)
    initialization.setup_resultdb(g.cfg.setting.database_file)
    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        pd.read_csv("tests/test_data/saki_member.csv").to_sql(
            name="member",
            con=conn,
            if_exists="append",
            index=False,
        )
        pd.read_csv("tests/test_data/saki_team.csv").to_sql(
            name="team",
            con=conn,
            if_exists="append",
            index=False,
        )
        cur = conn.execute("select name from member where id != 0;")
        rows = cur.fetchall()
        for name in [dict(row).get("name") for row in rows]:
            conn.execute(
                "insert into alias(name, member) values (?, ?);",
                (
                    name,
                    name,
                ),
            )
        conn.commit()

    lookup.read_memberslist()
