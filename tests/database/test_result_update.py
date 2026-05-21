"""
tests/database/test_result_update.py
"""

import sys
from contextlib import closing

import pytest

import libs.global_value as g
from integrations import factory
from libs.bootstrap import configuration, initialization
from libs.domain import modify
from libs.domain.score import GameResult
from libs.functions import validator
from libs.types import ServiceType
from libs.utils import dbutil
from libs.utils.timekit import ExtendedDatetime as ExtDt
from tests.database import param_data


@pytest.mark.parametrize(
    "draw_split, game_result, get_point, get_rank",
    list(param_data.score_insert_case_01.values()),
    ids=list(param_data.score_insert_case_01.keys()),
)
def test_score_insert(draw_split: bool, game_result: str, get_point: dict[str, float], get_rank: dict[str, int], monkeypatch: pytest.MonkeyPatch) -> None:
    """スコア登録テスト"""
    monkeypatch.setattr(sys, "argv", ["progname", "--config=tests/testdata/empty.ini"])
    configuration.setup(init_db=False)
    g.cfg.setting.database_file = "memdb1?mode=memory&cache=shared"  # DB差し替え
    initialization.setup_resultdb(g.cfg.setting.database_file)
    g.adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)
    g.cfg.selected_service = ServiceType.STANDARD_IO

    m = g.adapter.parser()
    m.data.text = game_result
    m.data.event_ts = ExtDt().format(ExtDt.FMT.TS)

    score_data = GameResult(**validator.check_score(m))
    score_data.set(rule_version="test", draw_split=draw_split)
    score_data.calc()
    assert score_data.has_valid_data()
    modify.db_insert(score_data, m)

    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        cur = conn.execute("select * from result where ts=?;", (m.data.event_ts,))
        db_data = dict(cur.fetchone())
        assert db_data is not None

    db_point = {k: v for k, v in db_data.items() if str(k).endswith("_point")}
    db_rank = {k: v for k, v in db_data.items() if str(k).endswith("_rank")}
    print(m.data.event_ts, db_point, db_rank)
    assert db_point == get_point
    assert db_rank == get_rank
