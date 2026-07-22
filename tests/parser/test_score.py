"""
得点入力の解析とポイント計算を検証するテスト。
"""

import sys
from typing import Any

import pytest

import libs.global_value as g
from integrations import factory
from libs.bootstrap import configuration, initialization
from libs.domain.score import GameResult
from libs.functions import validator
from libs.types import ServiceType
from tests.parser import param_data


@pytest.mark.parametrize(
    "input_str, result_dict, get_point",
    list(param_data.score_pattern.values()),
    ids=list(param_data.score_pattern.keys()),
)
def test_score_report(
    input_str: str,
    result_dict: dict[str, Any],
    get_point: dict[str, float],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    得点入力文字列の解析結果と計算結果を検証する。

    抽出済み項目と point 計算値を期待データと照合し、再計算時の安定性も確認する。

    Args:
        input_str (str): 得点報告の入力文字列。
        result_dict (dict[str, Any]): 期待する抽出結果辞書。
        get_point (dict[str, float]): 期待するポイント辞書。
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/test_data/empty.ini"])
    configuration.setup(init_db=False)
    g.cfg.setting.database_file = "memdb1?mode=memory&cache=shared"  # DB差し替え
    initialization.setup_resultdb(g.cfg.setting.database_file)
    g.adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)
    g.cfg.selected_service = ServiceType.STANDARD_IO

    m = g.adapter.parser()
    m.data.text = input_str
    m.data.event_ts = "1234567890.123456"

    result = GameResult(**validator.check_score(m))
    result.set(rule_version="test")
    result.calc()
    print(vars(result))
    chk_dict: dict[str, Any] = {}
    if result.has_valid_data():
        chk_dict.update({k: v for k, v in result.to_dict().items() if str(k).endswith("_name")})
        chk_dict.update({k: v for k, v in result.to_dict().items() if str(k).endswith("_str")})
        chk_dict.update({"comment": result.comment})
    print("in:", input_str)
    print("score data:", chk_dict, "->", result_dict)
    assert chk_dict == result_dict

    if result.has_valid_data():
        for x in range(3):
            result.calc(**result.to_dict())
            print("point:", x, result.to_list("point"))
            assert result.p1.point == get_point["p1_point"]
            assert result.p2.point == get_point["p2_point"]
            assert result.p3.point == get_point["p3_point"]
            assert result.p4.point == get_point["p4_point"]


@pytest.mark.parametrize(
    "rpoint_list, point_dict, rank_dict",
    list(param_data.point_calculation_pattern01.values()),
    ids=list(param_data.point_calculation_pattern01.keys()),
)
def test_point_calc_seat(
    rpoint_list: list[str],
    point_dict: dict[str, float],
    rank_dict: dict[str, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    同点時に席順優先ルールで順位・ポイントが決まることを検証する。

    draw_split=False 条件で point/rank と供託値が期待どおりかを確認する。

    Args:
        rpoint_list (list[str]): 各プレイヤーの素点入力文字列。
        point_dict (dict[str, float]): 期待するポイント辞書。
        rank_dict (dict[str, int]): 期待する順位辞書。
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/test_data/empty.ini"])
    configuration.setup(init_db=False)
    g.cfg.setting.database_file = "memdb1?mode=memory&cache=shared"  # DB差し替え
    initialization.setup_resultdb(g.cfg.setting.database_file)
    g.adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)
    g.cfg.selected_service = ServiceType.STANDARD_IO

    rule = g.cfg.rule.to_dict(g.cfg.rule.get_version(4)[0])
    result = GameResult(
        ts="1234567890.123456",
        rule_version="test",
        draw_split=False,
        return_point=rule["return_point"],
        origin_point=rule["origin_point"],
        p1_name="東家",
        p1_str=rpoint_list[0],
        p2_name="南家",
        p2_str=rpoint_list[1],
        p3_name="西家",
        p3_str=rpoint_list[2],
        p4_name="北家",
        p4_str=rpoint_list[3],
    )
    result.calc()

    ret_point = {k: v for k, v in result.to_dict().items() if str(k).endswith("_point")}
    ret_rank = {k: v for k, v in result.to_dict().items() if str(k).endswith("_rank")}

    assert ret_point == point_dict
    assert ret_rank == rank_dict
    assert result.deposit == 0


@pytest.mark.parametrize(
    "rpoint_list, point_dict, rank_dict",
    list(param_data.point_calculation_pattern02.values()),
    ids=list(param_data.point_calculation_pattern02.keys()),
)
def test_point_calc_division(
    rpoint_list: list[str],
    point_dict: dict[str, float],
    rank_dict: dict[str, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    同点時に山分けルールで順位・ポイントが決まることを検証する。

    draw_split=True 条件で point/rank と供託値が期待どおりかを確認する。

    Args:
        rpoint_list (list[str]): 各プレイヤーの素点入力文字列。
        point_dict (dict[str, float]): 期待するポイント辞書。
        rank_dict (dict[str, int]): 期待する順位辞書。
        monkeypatch (pytest.MonkeyPatch): 実行時引数を差し替えるためのpytestフィクスチャ。

    """
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/test_data/empty.ini"])
    configuration.setup(init_db=False)
    g.cfg.setting.database_file = "memdb1?mode=memory&cache=shared"  # DB差し替え
    initialization.setup_resultdb(g.cfg.setting.database_file)
    g.adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)
    g.cfg.selected_service = ServiceType.STANDARD_IO

    rule = g.cfg.rule.to_dict(g.cfg.rule.get_version(4)[0])
    result = GameResult(
        ts="1234567890.123456",
        rule_version="test",
        draw_split=True,
        return_point=rule["return_point"],
        origin_point=rule["origin_point"],
        p1_name="東家",
        p1_str=rpoint_list[0],
        p2_name="南家",
        p2_str=rpoint_list[1],
        p3_name="西家",
        p3_str=rpoint_list[2],
        p4_name="北家",
        p4_str=rpoint_list[3],
    )
    result.calc()

    ret_point = {k: v for k, v in result.to_dict().items() if str(k).endswith("_point")}
    ret_rank = {k: v for k, v in result.to_dict().items() if str(k).endswith("_rank")}

    assert ret_point == point_dict
    assert ret_rank == rank_dict
    assert result.deposit == 0
