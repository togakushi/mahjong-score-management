#!/usr/bin/env python3
"""
test.py
"""

import configparser
import random
import re
import shutil
from pathlib import Path
from pprint import pprint
from typing import TYPE_CHECKING, Any

import libs.global_value as g
from integrations import factory
from libs.bootstrap import configuration
from libs.bootstrap.configuration import arg_parser
from libs.commands import deliverables
from libs.commands.deliverables.text_assembly import help_message
from libs.domain.command import CommandParser
from libs.types import ServiceType
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def test_pattern(flag: dict[str, Any], test_case: str, sec: str, pattern: str, argument: str) -> None:
    """
    テストケース実行

    Args:
        flag (dict[str, Any]): フラグ格納辞書
        test_case (str): テストケース
        sec (str): 定義セクション
        pattern (str): 実行パターン
        argument (str): コマンドライン引数

    """

    def graph_point(m: "MessageParserProtocol") -> None:
        """
        ポイント推移グラフを生成する。

        プレイヤー数に応じて描画先を切り替え、単独指定時は個人推移、
        複数指定時はサマリ推移を出力する。

        Args:
            m (MessageParserProtocol): 描画対象の入力情報を保持するメッセージパーサ。

        """
        if len(g.params.player_list) == 1:
            deliverables.graph_personal.plot(m)
            pprint(
                [
                    "exec: deliverables.graph_personal.plot()",
                    f"{g.params=}" if flag.get("dump") else "g.params={...}",
                ],
                width=120,
            )
        else:
            deliverables.graph_summary.point_plot(m)
            pprint(
                [
                    "exec: deliverables.graph_summary.point_plot()",
                    f"{g.params=}" if flag.get("dump") else "g.params={...}",
                ],
                width=120,
            )

    def graph_rank(m: "MessageParserProtocol") -> None:
        """
        順位変動グラフを生成する。

        サマリ描画関数を呼び出し、順位推移の確認に必要な出力を行う。

        Args:
            m (MessageParserProtocol): 描画対象の入力情報を保持するメッセージパーサ。

        """
        deliverables.graph_summary.point_plot(m)
        pprint(
            [
                "exec: deliverables.graph_summary.point_plot()",
                f"{g.params=}" if flag.get("dump") else "g.params={...}",
            ],
            width=120,
        )

    def graph_statistics(m: "MessageParserProtocol") -> None:
        """
        個人成績の統計グラフを生成する。

        統計オプションが有効なケースで利用し、実行パラメータの確認出力も行う。

        Args:
            m (MessageParserProtocol): 描画対象の入力情報を保持するメッセージパーサ。

        """
        deliverables.graph_personal.statistics_plot(m)
        pprint(
            [
                "exec: deliverables.graph_personal.statistics_plot()",
                f"{g.params=}" if flag.get("dump") else "g.params={...}",
            ],
            width=120,
        )

    # ---------------------------------------------------------------------------------------------
    configuration.setup()
    adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)
    m = adapter.parser()
    target_loop: list[str] = []

    if flag.get("target_loop"):
        target_loop += flag.get("target_player", [])
        target_loop += flag.get("target_team", [])
    else:
        target_loop = ["once"]
        argument += " ".join(flag.get("target_player", []))
        argument += " ".join(flag.get("target_team", []))

    for loop in target_loop:
        add_argument = argument.split()

        # 追加オプション
        pre_params = CommandParser().analysis_argument(add_argument).flags
        if flag.get("target_loop"):
            add_argument.append(f"{loop}")

        if flag.get("save"):
            if pre_params.get("filename"):
                pass
            else:
                if flag.get("target_loop"):
                    add_argument.append(f"filename:{sec}_{pattern}_{loop}")
                else:
                    add_argument.append(f"filename:{sec}_{pattern}")

        print("-" * 120)
        print(f"{pattern=} argument={add_argument}")

        match test_case:
            case "skip":
                pass

            case "member":
                pprint(g.cfg.member.info)
                pprint(g.cfg.team.info)

            case "help":
                help_message(m)
                pprint(
                    [
                        "exec: help.help_message()",
                        f"{g.params=}" if flag.get("dump") else "g.params={...}",
                    ],
                    width=120,
                )

            case "summary":
                m.data.text = f"{g.cfg.summary.commandwords_list()[0]} {' '.join(add_argument)}"
                g.params = dictutil.placeholder(g.cfg.summary, m)
                deliverables.results_detail.aggregation(m)
                pprint(
                    [
                        "exec: deliverables.results.aggregation()",
                        f"{g.params=}" if flag.get("dump") else "g.params={...}",
                    ],
                    width=120,
                )

            case "graph":
                m.data.text = f"{g.cfg.summary.commandwords_list()[0]} {' '.join(add_argument)}"
                g.params = dictutil.placeholder(g.cfg.summary, m)
                if g.params.filename:
                    save_filename = g.params.filename
                    g.params.filename = f"{save_filename}_point"
                    graph_point(m)

                    g.params.filename = f"{save_filename}_rank"
                    graph_rank(m)
                    if g.params.statistics:
                        g.params.filename = f"{save_filename}"
                        graph_statistics(m)
                else:
                    g.params.filename = f"point_{sec}_{pattern}"
                    graph_point(m)
                    g.params.filename = f"rank_{sec}_{pattern}"
                    graph_rank(m)
                    if g.params.statistics:
                        g.params.filename = f"statistics_{sec}_{pattern}"
                        graph_statistics(m)

            case "graph_point":
                m.data.text = f"{g.cfg.summary.commandwords_list()[0]} {' '.join(add_argument)}"
                g.params = dictutil.placeholder(g.cfg.summary, m)
                graph_point(m)

            case "graph_rank":
                m.data.text = f"{g.cfg.summary.commandwords_list()[0]} {' '.join(add_argument)}"
                g.params = dictutil.placeholder(g.cfg.summary, m)
                graph_rank(m)

            case "graph_statistics":
                m.data.text = f"{g.cfg.summary.commandwords_list()[0]} {' '.join(add_argument)}"
                g.params = dictutil.placeholder(g.cfg.summary, m)
                graph_statistics(m)

            case "ranking":
                m.data.text = f"{g.cfg.analysis.commandwords_list()[0]} {' '.join(add_argument)}"
                g.params = dictutil.placeholder(g.cfg.analysis, m)
                deliverables.ranking_calc.aggregation(m)

                pprint(
                    [
                        "exec: deliverables.ranking_calc.aggregation()",
                        f"{g.params=}" if flag.get("dump") else "g.params={...}",
                    ],
                    width=120,
                )

            case "rating":
                m.data.text = f"{g.cfg.analysis.commandwords_list()[0]} {' '.join(add_argument)}"
                g.params = dictutil.placeholder(g.cfg.summary, m)
                deliverables.graph_rating.plot(m)
                pprint(
                    [
                        "exec: deliverables.graph_rating.plot()",
                        f"{g.params=}" if flag.get("dump") else "g.params={...}",
                    ],
                    width=120,
                )


def main() -> None:
    """
    テストケース定義に従ってパターン実行を行う。

    設定ファイルを読み込み、対象パターンごとに前処理を適用したうえで test_pattern を呼び出す。

    """
    g.args = arg_parser()
    assert isinstance(g.args.testcase, Path)

    configuration.setup()
    if g.cfg.setting.work_dir.is_dir():
        shutil.rmtree(g.cfg.setting.work_dir)
    g.cfg.setting.work_dir.mkdir()
    test_conf = configparser.ConfigParser()
    test_conf.read(g.args.testcase, encoding="utf-8")

    flag: dict[str, Any] = {}

    for sec in test_conf.sections():
        print("=" * 120)
        print(f"[TEST CASE] {sec}")
        test_case = str()
        always_keyword = str()
        flag.clear()
        flag.update(target_player=[])
        flag.update(target_team=[])
        flag.update(target_loop=False)
        flag.update(dump=test_conf["default"].getboolean("dump", False))
        flag.update(save=test_conf["default"].getboolean("save", False))

        for pattern, value in test_conf[sec].items():
            flag.update(filename=f"{sec}_{pattern}")
            match pattern:
                case s if re.match(r"^case", s):
                    test_case = value
                    continue
                case "target_player":
                    flag["target_team"].clear()
                    choice_list = g.cfg.member.lists
                    for x in range(int(value)):
                        if not choice_list:
                            break
                        choice_name = random.choice(choice_list)
                        flag["target_player"].append(choice_name)
                        choice_list.remove(choice_name)
                    continue
                case "target_team":
                    flag["target_player"].clear()
                    choice_list = g.cfg.team.lists
                    for _ in range(int(value)):
                        if not choice_list:
                            break
                        choice_name = random.choice(choice_list)
                        flag["target_team"].append(choice_name)
                        choice_list.remove(choice_name)
                    continue
                case "target_loop":
                    flag.update(target_loop=test_conf[sec].getboolean("target_loop"))
                    continue
                case s if re.match(r"^always_keyword", s):
                    always_keyword = value
                    print("always_keyword:", always_keyword)
                    continue
                case "save":
                    flag.update(save=test_conf[sec].getboolean("save"))
                    continue

            argument = f"{value} {always_keyword} "
            if test_conf[sec].getboolean("config", False):
                pprint(["*** config ***", vars(g.cfg)], width=120)

            test_pattern(flag, test_case, sec, pattern, argument)


if __name__ == "__main__":
    main()
