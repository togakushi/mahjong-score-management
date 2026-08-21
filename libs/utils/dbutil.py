"""
libs/utils/dbutil.py
"""

import logging
import sqlite3
from contextlib import closing
from importlib.resources import files
from typing import TYPE_CHECKING, Any, Optional, Union

import libs.global_value as g

if TYPE_CHECKING:
    from pathlib import Path


def connection(database_path: Union["Path", str]) -> sqlite3.Connection:
    """
    DB接続共通処理

    Args:
        database_path (Union[Path, str]): データベースファイル

    Returns:
        sqlite3.Connection: オブジェクト

    """
    conn = sqlite3.connect(
        database=f"file:{database_path}",
        # detect_types=sqlite3.PARSE_DECLTYPES,
        uri=True,
    )
    conn.row_factory = sqlite3.Row

    return conn


def execute(query: str, params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    """
    クエリ実行

    Args:
        query (str): 実行クエリ
        params (dict[str,Any], optional): プレースホルダ

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

    with closing(connection(g.cfg.setting.database_file)) as conn:
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


def query(keyword: str) -> str:
    """
    SQLクエリを返す

    Args:
        keyword (str): SQL選択キーワード

    Raises:
        ValueError: 未定義のキーワード

    Returns:
        str: SQL文

    """
    sql_tables: dict[str, str] = {
        # テーブル作成
        "CREATE_TABLE_MEMBER": "table/member.sql",
        "CREATE_TABLE_ALIAS": "table/alias.sql",
        "CREATE_TABLE_TEAM": "table/team.sql",
        "CREATE_TABLE_RESULT": "table/result.sql",
        "CREATE_TABLE_REMARKS": "table/remarks.sql",
        "CREATE_TABLE_WORDS": "table/words.sql",
        "CREATE_TABLE_RULE": "table/rule.sql",
        # VIEW作成
        "CREATE_VIEW_INDIVIDUAL_RESULTS": "view/individual_results.sql",
        "CREATE_VIEW_GAME_RESULTS": "view/game_results.sql",
        "CREATE_VIEW_GAME_INFO": "view/game_info.sql",
        "CREATE_VIEW_REGULATIONS": "view/regulations.sql",
        # INDEX作成
        "CREATE_INDEX": "table/index.sql",
        # 情報取得
        "GAME_INFO": "game.info.sql",
        "RESULTS_INFO": "results.info.sql",
        "MEMBER_INFO": "member.info.sql",
        "TEAM_INFO": "team.info.sql",
        "REMARKS_INFO": "remarks.info.sql",
        "RECORD_INFO": "record.info.sql",
        "RANK_INFO": "rank.info.sql",
        # 集計
        "SUMMARY_GAMEDATA": "summary/gamedata.sql",
        "SUMMARY_DETAILS": "summary/details.sql",
        "SUMMARY_DETAILS2": "summary/details2.sql",
        "SUMMARY_RESULTS": "summary/results.sql",
        "SUMMARY_CONSECUTIVE": "summary/consecutive.sql",
        "SUMMARY_TOTAL": "summary/total.sql",
        "SUMMARY_VERSUS_MATRIX": "summary/versus_matrix.sql",
        "RANKING_RESULTS": "ranking/results.sql",
        "RANKING_RATINGS": "ranking/ratings.sql",
        "REPORT_PERSONAL_DATA": "report/personal_data.sql",
        "REPORT_COUNT_DATA": "report/count_data.sql",
        "REPORT_GAME_STATISTICS": "report/game_statistics.sql",
        "REPORT_RESULTS_LIST": "report/results_list.sql",
        "REPORT_WINNER": "report/winner.sql",
        "REPORT_MATRIX_TABLE": "report/matrix_table.sql",
        "REPORT_COUNT_MOVING": "report/count_moving.sql",
        #
        "RESULT_INSERT": "general/result_insert.sql",
        "RESULT_UPDATE": "general/result_update.sql",
        "RESULT_DELETE": "general/result_delete.sql",
        #
        "REMARKS_SELECT": "general/remarks_select.sql",
        "REMARKS_INSERT": "general/remarks_insert.sql",
        "REMARKS_DELETE_ALL": "general/remarks_delete_all.sql",
        "REMARKS_DELETE_ONE": "general/remarks_delete_one.sql",
        "REMARKS_DELETE_COMPAR": "general/remarks_delete_compar.sql",
        #
        "WORDS_INSERT": "general/words_insert.sql",
        #
        "SELECT_ALL_RESULTS": "general/select_all_results.sql",
    }

    if query_path := sql_tables.get(keyword):
        with open(str(files("files.queries").joinpath(query_path)), "r", encoding="utf-8") as queryfile:
            return str(queryfile.read()).strip()
    else:
        raise ValueError(f"Unknown keyword: {keyword}")


def table_info(conn: sqlite3.Connection, table_name: str) -> dict[str, Any]:
    """
    テーブルのスキーマを取得して辞書で返す

    Args:
        conn (sqlite3.Connection): オブジェクト
        table_name (str): テーブル名

    Returns:
        dict[str, Any]: スキーマ

    """
    rows = conn.execute(f"pragma table_info('{table_name}');")
    schema = {row["name"]: dict(row) for row in rows.fetchall()}

    return schema
