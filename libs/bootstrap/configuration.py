"""
libs/bootstrap/configuration.py
"""

import argparse
import logging
import os
import shutil
import sys
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import libs.commands.graph.entry
import libs.commands.help.entry
import libs.commands.ranking.entry
import libs.commands.report.entry
import libs.commands.results.entry
import libs.global_value as g
from integrations import factory
from libs.bootstrap.app_config import AppConfig
from libs.commands.registry import member, team
from libs.data import initialization, lookup
from libs.functions.compose import text_item
from libs.types import Args, StyleOptions

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def set_loglevel() -> None:
    """ログレベル追加"""
    # DEBUG : 10
    # INFO : 20
    # WARNING : 30
    # ERROR : 40
    # CRITICAL : 50

    # TRACE
    logging.TRACE = 5  # type: ignore
    logging.trace = partial(logging.log, logging.TRACE)  # type: ignore
    logging.addLevelName(logging.TRACE, "TRACE")  # type: ignore


def arg_parser() -> Args:
    """
    コマンドライン解析

    Returns:
        Args : ArgumentParserオブジェクト

    """
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
    )

    p.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.ini"),
        help="設定ファイル(default: %(default)s)",
    )
    p.add_argument(
        "--profile",
        help=argparse.SUPPRESS,
    )
    p.add_argument(
        "-s",
        "--service",
        choices=[
            "slack",
            "discord",
            "standard_io",
            "std",
            "web",
            "flask",
        ],
        type=str,
        default="slack",
        help="連携先サービス",
    )

    logging_group = p.add_argument_group("logging options")
    logging_group.add_argument(
        "-d",
        "--debug",
        action="count",
        default=0,
        help="デバッグレベル(-d, -dd)",
    )
    logging_group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="動作ログ出力レベル(-v, -vv, -vvv)",
    )
    logging_group.add_argument(
        "--moderate",
        action="store_true",
        help="ログレベルがエラー以下のもを非表示",
    )
    logging_group.add_argument(
        "--notime",
        action="store_true",
        help="ログフォーマットから日時を削除",
    )

    match os.path.basename(sys.argv[0]):
        case "app.py":
            service_stdio = p.add_argument_group("Only allowed when --service=standard_io")
            service_stdio.add_argument(
                "--text",
                type=str,
                help="input text strings",
            )
            service_web = p.add_argument_group("Only allowed when --service=web")
            service_web.add_argument(
                "--host",
                type=str,
                default="127.0.0.1",
                help="listen  address(default: %(default)s)",
            )
            service_web.add_argument(
                "--port",
                type=int,
                default=8000,
                help="bind port(default: %(default)s)",
            )
        case "dbtools.py":  # dbtools専用オプション
            required = p.add_argument_group("Required options(amutually exclusive)")
            exclusive = required.add_mutually_exclusive_group()
            exclusive.add_argument(
                "--compar",
                action="store_true",
                help="データ突合",
            )
            exclusive.add_argument(
                "--unification",
                type=Path,
                nargs="?",
                const="rename.ini",
                help="ファイルの内容に従って記録済みのメンバー名を修正する(default: %(const)s)",
            )
            exclusive.add_argument(
                "--recalculation",
                action="store_true",
                help="ポイント再計算",
            )
            exclusive.add_argument(
                "--export",
                dest="export_data",
                type=str,
                nargs="?",
                const="export",
                metavar="PREFIX",
                help="メンバー設定情報をエクスポート(default prefix: %(const)s)",
            )
            exclusive.add_argument(
                "--import",
                dest="import_data",
                type=str,
                nargs="?",
                const="export",
                metavar="PREFIX",
                help="メンバー設定情報をインポート(default prefix: %(const)s)",
            )
            exclusive.add_argument(
                "--vacuum",
                action="store_true",
                help="database vacuum",
            )
            exclusive.add_argument(
                "--gen-test-data",
                type=int,
                dest="gen_test_data",
                nargs="?",
                const=1,
                default=None,
                metavar="count",
                help="テスト用サンプルデータ生成(count=生成回数, default: %(const)s)",
            )
        case "test.py":  # 動作テスト用オプション
            p.add_argument(
                "-t",
                "--testcase",
                dest="testcase",
                type=Path,
            )

    # 非表示オプション（外部ツールのオプション受け入れ）
    hidden_group = p.add_argument_group("hidden options")
    hidden_group.add_argument(
        "--rootdir",
        help=argparse.SUPPRESS,
    )

    return cast(Args, p.parse_args(namespace=Args))


def setup(init_db: bool = True) -> None:
    """
    設定ファイル読み込み処理

    Args:
        init_db (bool, optional): resultdbの初期化処理を行う Defaults to True.

    """
    set_loglevel()

    g.args = arg_parser()

    # ログフォーマット
    if g.args.notime:
        fmt = ""
    else:
        fmt = "[%(asctime)s]"

    # デバッグレベル
    match g.args.debug:
        case 1:
            fmt += "[%(levelname)s][%(module)s:%(funcName)s] %(message)s"
            logging.basicConfig(level=logging.DEBUG, format=fmt)
            logging.info("DEBUG MODE")
        case 2:
            fmt += "[%(levelname)s][%(module)s:%(funcName)s] %(message)s"
            logging.basicConfig(level=logging.TRACE, format=fmt)  # type: ignore
            logging.info("TRACE MODE")
        case _:
            fmt += "[%(levelname)s][%(module)s:%(funcName)s] %(message)s"
            if g.args.moderate:
                logging.basicConfig(level=logging.WARNING, format=fmt)
            else:
                logging.basicConfig(level=logging.INFO, format=fmt)

    g.cfg = AppConfig(g.args.config)

    # 連携サービス
    match g.args.service:
        case "slack":
            g.cfg.selected_service = "slack"
        case "discord":
            g.cfg.selected_service = "discord"
        case "standard_io" | "std":
            g.cfg.selected_service = "standard_io"
        case "web" | "flask":
            g.cfg.selected_service = "web"
        case _:
            sys.exit()

    if not hasattr(g.args, "testcase"):
        g.args.testcase = None
    else:
        g.cfg.selected_service = "standard_io"

    g.adapter = factory.select_adapter(g.cfg.selected_service, g.cfg)

    # 設定情報
    logging.info("config: %s", g.cfg.config_file.absolute())
    logging.info(
        "service: %s, graph_library: %s, time_adjust: %sh",
        g.cfg.selected_service,
        g.adapter.conf.plotting_backend,
        g.cfg.setting.time_adjust,
    )

    # ディレクトリ作成
    if not g.args.testcase:
        if g.cfg.setting.work_dir.is_dir():
            shutil.rmtree(g.cfg.setting.work_dir)
    try:
        g.cfg.setting.work_dir.mkdir(exist_ok=True)
    except FileExistsError as err:
        sys.exit(str(err))

    if isinstance(g.cfg.setting.backup_dir, Path):
        try:
            g.cfg.setting.backup_dir.mkdir(exist_ok=True)
        except FileExistsError as err:
            sys.exit(str(err))

    # DB初期化
    initialization.main(init_db)
    lookup.read_memberslist()

    register()

    # メモ記録ワード登録
    if g.cfg.setting.remarks_suffix:
        for rule_version in g.cfg.rule.rule_list:
            keywords = [word for word, rule in g.cfg.rule.keyword_mapping.items() if rule == rule_version]
            if keywords:
                g.cfg.rule.data[rule_version].remarks_words.extend([f"{rule}{suffix}" for rule in keywords for suffix in g.cfg.setting.remarks_suffix])
    else:
        for rule_version in g.cfg.rule.rule_list:
            g.cfg.rule.data[rule_version].remarks_words.append(g.cfg.setting.remarks_word)

    # キーワード重複チェック
    g.cfg.rule.check(
        chk_commands=set(
            g.cfg.results.commandword
            + g.cfg.graph.commandword
            + g.cfg.ranking.commandword
            + g.cfg.report.commandword
            + g.cfg.help.commandword
            + list(g.keyword_dispatcher)
        ),
        chk_members=set(lookup.enumeration_all_members()),
        default_rule=g.cfg.setting.default_rule,
    )


def register() -> None:
    """ディスパッチテーブル登録"""

    def dispatch_download(m: "MessageParserProtocol") -> None:
        m.set_message(g.cfg.setting.database_file, StyleOptions(title="成績記録DB"))

    def dispatch_members_list(m: "MessageParserProtocol") -> None:
        m.set_message(text_item.get_members_list(), StyleOptions(title="登録済みメンバー", codeblock=True))
        m.post.ts = m.data.event_ts
        m.post.thread_title = "登録済みメンバー"

    def dispatch_team_list(m: "MessageParserProtocol") -> None:
        m.set_message(text_item.get_team_list(), StyleOptions(title="登録済みチーム", codeblock=True))
        m.post.ts = m.data.event_ts
        m.post.thread_title = "登録済みチーム"

    def dispatch_member_append(m: "MessageParserProtocol") -> None:
        m.set_message(member.append(m.argument), StyleOptions(title="メンバー追加", key_title=False))

    def dispatch_member_remove(m: "MessageParserProtocol") -> None:
        m.set_message(member.remove(m.argument), StyleOptions(title="メンバー削除", key_title=False))

    def dispatch_team_create(m: "MessageParserProtocol") -> None:
        m.set_message(team.create(m.argument), StyleOptions(title="チーム作成", key_title=False))

    def dispatch_team_delete(m: "MessageParserProtocol") -> None:
        m.set_message(team.delete(m.argument), StyleOptions(title="チーム削除", key_title=False))

    def dispatch_team_append(m: "MessageParserProtocol") -> None:
        m.set_message(team.append(m.argument), StyleOptions(title="チーム所属", key_title=False))

    def dispatch_team_remove(m: "MessageParserProtocol") -> None:
        m.set_message(team.remove(m.argument), StyleOptions(title="チーム脱退", key_title=False))

    def dispatch_team_clear(m: "MessageParserProtocol") -> None:
        m.set_message(team.clear(), StyleOptions(title="全チーム削除", key_title=False))

    dispatch_table: dict[str, Any] = {
        "results": libs.commands.results.entry.main,
        "graph": libs.commands.graph.entry.main,
        "ranking": libs.commands.ranking.entry.main,
        "report": libs.commands.report.entry.main,
        "help": libs.commands.help.entry.main,
        "member": dispatch_members_list,
        "team": dispatch_team_list,
        "team_list": dispatch_team_list,
        "download": dispatch_download,
        "add": dispatch_member_append,
        "delete": dispatch_member_remove,
        "team_create": dispatch_team_create,
        "team_del": dispatch_team_delete,
        "team_add": dispatch_team_append,
        "team_remove": dispatch_team_remove,
        "team_clear": dispatch_team_clear,
    }

    commandword_list: list[str]
    for command, ep in dispatch_table.items():
        # 呼び出しキーワード登録
        if hasattr(g.cfg, command):
            sub_command = getattr(g.cfg, command)
            commandword_list = []
            if hasattr(sub_command, "command_suffix"):  # コマンドサフィックス登録
                for keyword in g.cfg.rule.keyword_mapping:
                    for suffix in sub_command.command_suffix:
                        commandword_list.append(f"{keyword}{suffix}")
            if hasattr(sub_command, "commandword") and not commandword_list:
                for commandword in sub_command.commandword:
                    commandword_list.append(commandword)
            for commandword in commandword_list:
                g.keyword_dispatcher.update({commandword: ep})
        # スラッシュコマンド登録
        if hasattr(g.cfg.alias, command):
            for alias in cast(list[str], getattr(g.cfg.alias, command)):
                g.command_dispatcher.update({alias: ep})

    # サービス別コマンド登録
    g.command_dispatcher.update(g.adapter.conf.command_dispatcher)
    g.keyword_dispatcher.update(g.adapter.conf.keyword_dispatcher)

    logging.debug("keyword_dispatcher:\n%s", "\n".join([f"\t{k}: {v}" for k, v in g.keyword_dispatcher.items()]))
    logging.debug("command_dispatcher:\n%s", "\n".join([f"\t{k}: {v}" for k, v in g.command_dispatcher.items()]))
