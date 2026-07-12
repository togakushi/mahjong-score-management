"""
動作フラグからキーワードディスパッチを検証するテスト。
"""

import random
import sys
from itertools import product

import pytest

import libs.global_value as g
from libs.bootstrap import configuration
from libs.commands.analysis import COMMAND_DISPATCHER as ANALYSIS_DISPATCHER
from libs.commands.summary import COMMAND_DISPATCHER as SUMMARY_DISPATCHER

ANALYSIS_CASES = list(product([False, True], repeat=7))
ANALYSIS_IDS = [
    (f"gr{int(f01)}_re{int(f02)}_ra{int(f03)}_vs{int(f04)}_st{int(f05)}_sc{int(f06)}_co{int(f07)}") for f01, f02, f03, f04, f05, f06, f07 in ANALYSIS_CASES
]

SUMMARY_CASES = list(product([False, True], repeat=4))
SUMMARY_IDS = [(f"gr{int(f01)}_or{int(f02)}_di{int(f03)}_vs{int(f04)}") for f01, f02, f03, f04 in SUMMARY_CASES]


@pytest.fixture(scope="module", autouse=True)
def initialize() -> None:
    """
    メッセージディスパッチ用パーサを初期化する。

    標準入出力アダプタを生成し、コマンド判定フラグを事前設定する。

    Args:
        None.

    """
    sys.argv = [
        "app.py",
        "--service=standard_io",
        "--config=tests/test_data/saki.ini",
    ]

    configuration.setup(init_db=False)


@pytest.mark.parametrize(
    "flg_graph, flg_report, flg_rating, flg_versus, flg_statistics, flg_score, flg_compar",
    ANALYSIS_CASES,
    ids=ANALYSIS_IDS,
)
@pytest.mark.parametrize("player_count", [0, 1, 2])
def test_analysis_command(
    flg_graph: bool,
    flg_report: bool,
    flg_rating: bool,
    flg_versus: bool,
    flg_statistics: bool,
    flg_score: bool,
    flg_compar: bool,
    player_count: int,
    initialize: None,
) -> None:
    """
    分析コマンドのルーティングを検証する。

    Args:
        flg_graph (bool): グラフオプション
        flg_report (bool): レポートオプション
        flg_rating (bool): レーティングオプション
        flg_versus (bool): 対戦オプション
        flg_statistics (bool): 統計オプション
        flg_score (bool): 素点オプション
        flg_compar (bool): 比較オプション
        player_count (int): ターゲットに指定される人数
        initialize (fixture): 初期化fixture
    """
    g.params.graph = flg_graph
    g.params.report = flg_report
    g.params.rating = flg_rating
    g.params.versus = flg_versus
    g.params.statistics = flg_statistics
    g.params.raw_score = flg_score
    g.params.comparisons = flg_compar
    if player_count:
        g.params.player_list = random.choices(g.cfg.member.lists, k=player_count)

    for command in ANALYSIS_DISPATCHER:
        if command.condition():
            print(f"{flg_graph=}, {flg_rating=}, {flg_report=}, {flg_score=}, {flg_statistics=}, {flg_versus=}, {flg_compar=}, {player_count=}", command.name)
            break


@pytest.mark.parametrize(
    "flg_graph, flg_order, flg_compar, flg_versus",
    SUMMARY_CASES,
    ids=SUMMARY_IDS,
)
@pytest.mark.parametrize("player_count", [0, 1, 2])
def test_summary_command(
    flg_graph: bool,
    flg_order: bool,
    flg_compar: bool,
    flg_versus: bool,
    player_count: int,
    initialize: None,
) -> None:
    """
    集計コマンドのルーティングを検証する。

    Args:
        flg_graph (bool): グラフオプション
        flg_order (bool): 順位オプション
        flg_compar (bool): 比較オプション
        flg_versus (bool): 対戦オプション
        player_count (int): ターゲットに指定される人数
        initialize (fixture): 初期化fixture
    """
    g.params.graph = flg_graph
    g.params.order = flg_order
    g.params.comparisons = flg_compar
    g.params.versus = flg_versus
    if player_count:
        g.params.player_list = random.choices(g.cfg.member.lists, k=player_count)

    for command in SUMMARY_DISPATCHER:
        if command.condition():
            print(f"{flg_graph=}, {flg_order=}, {flg_compar=}, {flg_versus=}, {player_count=}", command.name)
            break
