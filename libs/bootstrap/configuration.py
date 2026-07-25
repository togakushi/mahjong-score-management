"""
libs/bootstrap/configuration.py
"""

import argparse
import logging
import shutil
import sys
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import libs.global_value as g
from integrations import factory
from libs.bootstrap import initialization
from libs.bootstrap.app_config import AppConfig
from libs.commands.registry import member, team
from libs.domain.datamodels import Args
from libs.functions import lookup
from libs.types import ServiceType, StyleOptions

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
    prog_path = Path(sys.argv[0])
    project_data = lookup.get_toml_data()
    app_version = str(project_data.get("version", ""))
    app_description = str(project_data.get("description", ""))

    p = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
        allow_abbrev=False,
        description=f"{app_description}\nRelease Version: {app_version}",
    )

    p.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.ini"),
        help="設定ファイル(default: %(default)s)",
    )
    p.add_argument(
        "--no-cleanup",
        dest="no_cleanup",
        action="store_false",
        help="作業ディレクトリの内容を削除しない",
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

    match prog_path.name:
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
                type=str,
                nargs="*",
                metavar="RULE_VERSION",
                help="ポイント再計算(引数なし=全ルール, 引数あり=指定ルールのみ)",
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

    args, unknown = p.parse_known_args()
    if unknown and prog_path.name in ["app.py", "dbtools.py"]:
        p.print_usage()
        sys.exit(f"\ninvalid args: {unknown}")

    return cast(Args, args)


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
            g.cfg.selected_service = ServiceType.SLACK
        case "discord":
            g.cfg.selected_service = ServiceType.DISCORD
        case "standard_io" | "std":
            g.cfg.selected_service = ServiceType.STANDARD_IO
        case "web" | "flask":
            g.cfg.selected_service = ServiceType.WEB
        case _:
            sys.exit()

    if not hasattr(g.args, "testcase"):
        g.args.testcase = None
    else:
        g.cfg.selected_service = ServiceType.STANDARD_IO

    g.adapter = factory.select_adapter(g.cfg.selected_service, g.cfg)

    # ディレクトリ作成
    if not g.args.testcase:
        if g.cfg.setting.work_dir.is_dir() and g.args.no_cleanup:
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

    # 初期化
    initialization.main(init_db)
    lookup.read_memberslist()
    register()

    # キーワード重複チェック
    g.cfg.rule.check(
        chk_commands=set(
            g.cfg.rule.remarks_words
            + g.cfg.summary.commandwords_list
            + g.cfg.analysis.commandwords_list
            + g.cfg.help.commandwords_list
            + g.cfg.member.commandwords_list
            + g.cfg.team.commandwords_list
            + list(g.cfg.shortcut)
        ),
        chk_members=set(lookup.enumeration_all_members()),
        default_rule=g.cfg.setting.default_rule,
    )

    # 設定情報
    logging.info("main_config: %s", g.cfg.config_file.absolute())
    if g.cfg.setting.rule_config:
        logging.info("rule_config: %s", g.cfg.setting.rule_config.absolute())
    if isinstance(g.cfg.setting.database_file, Path):
        logging.info("resultdb: %s", g.cfg.setting.database_file.absolute())
    logging.info(
        "service: %s, graph_library: %s, time_adjust: %sh",
        g.cfg.selected_service,
        g.adapter.conf.plotting_backend,
        g.cfg.setting.time_adjust,
    )

    g.cfg.rule.info()

    drop_items = ["section", "default_commandword", "command_suffix", "main_parser", "section_proxy", "info"]
    logging.debug("setting: %s", g.cfg.setting.to_dict(drop_items))
    logging.debug("summary: %s", g.cfg.summary.to_dict(drop_items))
    logging.debug("analysis: %s", g.cfg.analysis.to_dict(drop_items))
    logging.debug("member: %s", g.cfg.member.to_dict(drop_items))
    logging.debug("team: %s", g.cfg.team.to_dict(drop_items))
    logging.debug("help: %s", g.cfg.help.to_dict(drop_items))
    logging.debug("rule_set: %s", vars(g.cfg.rule))
    logging.debug("alias: %s", vars(g.cfg.alias))


def register() -> None:
    """ディスパッチテーブル登録"""

    def dispatch_download(m: "MessageParserProtocol") -> None:
        m.set_message(g.cfg.setting.database_file, StyleOptions(title="成績記録DB"))

    def dispatch_members_list(m: "MessageParserProtocol") -> None:
        member.members_list(m)

    def dispatch_team_list(m: "MessageParserProtocol") -> None:
        team.team_list(m)

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

    # コマンド登録
    g.cfg.summary.register()
    g.cfg.analysis.register()
    g.cfg.help.register()
    g.cfg.member.register()
    g.cfg.team.register()
    g.command_dispatcher.update(g.adapter.conf.command_dispatcher)  # サービス別コマンド登録

    # スラッシュコマンド登録
    for command, ep in dispatch_table.items():
        if hasattr(g.cfg.alias, command):
            for alias in cast(list[str], getattr(g.cfg.alias, command)):
                g.command_dispatcher.update({alias: ep})
    g.keyword_dispatcher.update(g.adapter.conf.keyword_dispatcher)  # サービス別コマンド登録

    logging.debug("keyword_dispatcher:\n%s", "\n".join([f"\t{k}: {v}" for k, v in g.keyword_dispatcher.items()]))
    logging.debug("command_dispatcher:\n%s", "\n".join([f"\t{k}: {v}" for k, v in g.command_dispatcher.items()]))
