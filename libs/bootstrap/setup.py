"""
libs/bootstrap/setup.py
"""

import json
import logging
import os
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

import libs.global_value as g
from libs.utils import dbutil

if TYPE_CHECKING:
    from libs.types import GradeTableDict


def main(init_db: bool) -> None:
    """
    初期化処理

    Args:
        init_db (bool): DB初期化処理の実行有無

    """
    if init_db:
        resultdb(g.cfg.setting.database_file)  # DB初期化

    grade_table()  # 段位テーブル取り込み
    rule_data()  # ルールデータ取り込み
    regulations(g.cfg.setting.database_file)  # レギュレーション設定取り込み


def resultdb(database_file: Union[str, Path]) -> None:
    """
    DB初期化 & マイグレーション

    Args:
        database_file (Union[str, Path]): データベース接続パス

    """
    resultdb = dbutil.connection(database_file)
    memdb = dbutil.connection(":memory:")

    # 旧テーブル削除
    resultdb.execute("drop table if exists rule;")
    resultdb.execute("drop table if exists words;")

    table_list = {
        "member": "CREATE_TABLE_MEMBER",  # メンバー登録テーブル
        "alias": "CREATE_TABLE_ALIAS",  # 別名定義テーブル
        "team": "CREATE_TABLE_TEAM",  # チーム定義テーブル
        "result": "CREATE_TABLE_RESULT",  # データ取り込みテーブル
        "remarks": "CREATE_TABLE_REMARKS",  # メモ格納テーブル
        "words": "CREATE_TABLE_WORDS",  # レギュレーションワード登録テーブル
        "rule": "CREATE_TABLE_RULE",  # ルールセット登録テーブル
    }
    for table_name, keyword in table_list.items():
        # テーブル作成
        resultdb.execute(dbutil.query(keyword))
        memdb.execute(dbutil.query(keyword))

        # スキーマ比較
        actual_cols = dbutil.table_info(resultdb, table_name)
        expected_cols = dbutil.table_info(memdb, table_name)
        for col_name, col_data in expected_cols.items():
            if col_name not in actual_cols:
                # NOT NULL かつ DEFAULT 未指定だと追加できないので回避
                if col_data["notnull"] and col_data["dflt_value"] is None:
                    logging.warning(
                        "migration skip: table=%s, column=%s, reason='NOT NULL' and 'DEFAULT' unspecified",
                        table_name,
                        col_name,
                    )
                    continue
                col_type = col_data["type"]
                notnull = "NOT NULL" if col_data["notnull"] else ""
                dflt = f"DEFAULT {col_data['dflt_value']}" if col_data["dflt_value"] is not None else ""
                resultdb.execute(f"alter table {table_name} add column {col_name} {col_type} {notnull} {dflt};")
                logging.info("migration: table=%s, column=%s", table_name, col_name)

    # 追加カラムデータ更新
    resultdb.execute("update result set mode = 4 where mode isnull and p4_name != '' and p4_str != '';")

    # VIEW
    rows = resultdb.execute("select name from sqlite_master where type = 'view';")
    for row in rows.fetchall():
        resultdb.execute(f"drop view if exists '{row['name']}';")
    resultdb.execute(dbutil.query("CREATE_VIEW_INDIVIDUAL_RESULTS").replace("<time_adjust>", str(g.cfg.setting.time_adjust)))
    resultdb.execute(dbutil.query("CREATE_VIEW_GAME_RESULTS").replace("<time_adjust>", str(g.cfg.setting.time_adjust)))
    resultdb.execute(dbutil.query("CREATE_VIEW_GAME_INFO"))
    resultdb.execute(dbutil.query("CREATE_VIEW_REGULATIONS"))

    # INDEX
    resultdb.execute(dbutil.query("CREATE_INDEX"))

    # ゲスト設定チェック
    ret = resultdb.execute("select * from member where id=0;")
    data = ret.fetchall()

    if len(data) == 0:
        logging.info("ゲスト設定: %s", g.cfg.member.guest_name)
        sql = "insert into member (id, name) values (0, ?);"
        resultdb.execute(sql, (g.cfg.member.guest_name,))
    elif data[0][1] != g.cfg.member.guest_name:
        logging.warning("ゲスト修正: %s -> %s", data[0][1], g.cfg.member.guest_name)
        sql = "update member set name=? where id=0;"
        resultdb.execute(sql, (g.cfg.member.guest_name,))

    resultdb.commit()
    resultdb.close()
    memdb.close()


def rule_data() -> None:
    """ルールデータ取り込み"""

    # メイン設定ファイルから取り込み
    if g.cfg.main_parser.has_section("mahjong"):
        section_data = dict(g.cfg.main_parser["mahjong"])
        if rule_version := section_data.get("rule_version"):
            g.cfg.rule.data_set("mahjong", rule_data=section_data)

    # ルール設定ファイル探索 & 取り込み
    if g.cfg.setting.rule_config:
        if not g.cfg.setting.rule_config.exists():
            if (new_conf := g.cfg.config_dir / str(g.cfg.setting.rule_config)) and new_conf.exists():
                g.cfg.setting.rule_config = new_conf
            elif (new_conf := g.cfg.script_dir / str(g.cfg.setting.rule_config)) and new_conf.exists():
                g.cfg.setting.rule_config = new_conf
            elif (new_conf := Path.cwd() / str(g.cfg.setting.rule_config)) and new_conf.exists():
                g.cfg.setting.rule_config = new_conf
            else:
                g.cfg.setting.rule_config = None
        if g.cfg.setting.rule_config:
            g.cfg.rule.read_config(g.cfg.setting.rule_config)

    # ルールセットがなければプリセットから取り込み
    if not g.cfg.rule.rule_list:
        if (new_conf := g.cfg.config_dir / "files/default_rule.ini") and new_conf.exists():
            g.cfg.setting.rule_config = new_conf
        elif (new_conf := g.cfg.script_dir / "files/default_rule.ini") and new_conf.exists():
            g.cfg.setting.rule_config = new_conf

        if g.cfg.setting.rule_config:
            g.cfg.rule.read_config(g.cfg.setting.rule_config)
        else:
            raise TypeError("Preset not found.")

    # デフォルトルール定義
    if not g.cfg.setting.default_rule:
        g.cfg.setting.default_rule = g.cfg.rule.rule_list[0]

    # マッピング生成
    for rule_version in g.cfg.rule.rule_list:
        for keyword in g.cfg.rule.keywords(rule_version):
            g.cfg.rule.keyword_mapping.update({keyword: rule_version})

    if g.cfg.main_parser.has_section("keyword_mapping"):
        for keyword, rule_version in dict(g.cfg.main_parser["keyword_mapping"]).items():
            if not rule_version:
                g.cfg.rule.keyword_mapping.update({keyword: g.cfg.setting.default_rule})
            elif rule_version in g.cfg.rule.data:
                g.cfg.rule.keyword_mapping.update({keyword: rule_version})

    g.cfg.rule.status_update(g.params.placeholder())
    g.cfg.rule.remarks_words_update(g.cfg.setting.remarks_suffix)
    g.cfg.rule.register_to_database()


def regulations(database_file: Union[str, Path]) -> None:
    """
    レギュレーション設定取り込み

    Args:
        database_file (Union[str, Path]): データベース接続パス

    """

    def _db_set() -> None:
        params: dict[str, Any] = {}
        for k, v in parser.items(section):
            match k:
                case "yakuman_list":
                    words_list = {x.strip() for x in v.split(",")}
                    for word in words_list:
                        params = {"word": word, "type": 0, "ex_point": None, "rule_version": rule}
                        resultdb.execute(dbutil.query("WORDS_INSERT"), params)
                    logging.debug("regulations table(type0): %s", words_list)
                case "word_list":
                    words_list = {x.strip() for x in v.split(",")}
                    for word in words_list:
                        params = {"word": word, "type": 1, "ex_point": None, "rule_version": rule}
                        resultdb.execute(dbutil.query("WORDS_INSERT"), params)
                    logging.debug("regulations table(type1): %s", words_list)
                case _:
                    params = {"word": k.strip(), "type": regulation_type, "ex_point": int(v), "rule_version": rule}
                    resultdb.execute(dbutil.query("WORDS_INSERT"), params)
                    logging.debug("regulations table(type%s): %s, %s", regulation_type, params["word"], params["ex_point"])

    resultdb = dbutil.connection(database_file)
    resultdb.execute("delete from words;")

    for rule in g.cfg.rule.rule_list:
        # 個人レギュレーション
        regulation_type = 2
        section_patterns = [
            (g.cfg.rule.config, f"{rule}_regulations"),
            (g.cfg.rule.config, f"regulations_{rule}"),
            (g.cfg.main_parser, f"{rule}_regulations"),
            (g.cfg.main_parser, f"regulations_{rule}"),
            (g.cfg.main_parser, "regulations"),
        ]
        for parser, section in section_patterns:
            if section in parser.sections():
                _db_set()
                break

        # チームレギュレーション
        regulation_type = 3
        section_patterns = [
            (g.cfg.rule.config, f"{rule}_regulations_team"),
            (g.cfg.rule.config, f"regulations_team_{rule}"),
            (g.cfg.main_parser, f"{rule}_regulations_team"),
            (g.cfg.main_parser, f"regulations_team_{rule}"),
            (g.cfg.main_parser, "regulations_team"),
        ]
        for parser, section in section_patterns:
            if section in parser.sections():
                _db_set()
                break

    resultdb.commit()
    resultdb.close()


def grade_table() -> None:
    """段位テーブル取り込み"""
    # テーブル選択
    match table_name := g.cfg.badge.grade.table_name:
        case "":
            return
        case "mahjongsoul" | "雀魂":
            tbl_file = str(files("files.gradetable").joinpath("mahjongsoul.json"))
        case "tenho" | "天鳳":
            tbl_file = str(files("files.gradetable").joinpath("tenho.json"))
        case _:
            tbl_file = os.path.join(g.cfg.config_dir, table_name)
            if not os.path.isfile(tbl_file):
                return

    with open(tbl_file, encoding="utf-8") as f:
        try:
            tbl_data: "GradeTableDict" = json.load(f)
        except json.JSONDecodeError as err:
            logging.warning("JSONDecodeError: %s", err)
            return

    if not isinstance(tbl_list := tbl_data.get("table"), list):
        logging.warning("undefined key [table]")
        return

    for x in tbl_list:
        if isinstance(x, dict):
            x["demote"] = x.get("demote", True)
            if {"grade", "point", "acquisition", "demote"} == set(x.keys()):
                if not isinstance(x.get("grade"), str):
                    tbl_data = {}
                    break
                point = x.get("point")
                if not isinstance(point, list) or len(point) != 2:
                    logging.warning("point is not match")
                    tbl_data = {}
                    break
                acquisition = x.get("acquisition")
                if not isinstance(acquisition, list) or len(acquisition) != 4:
                    logging.warning("acquisition is not match")
                    tbl_data = {}
                    break
            else:
                logging.warning("undefined key [grade, point, acquisition]")
                tbl_data = {}
                break
        else:
            tbl_data = {}
            break

    g.cfg.badge.grade.table = tbl_data
