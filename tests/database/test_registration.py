"""
メンバー・チーム登録処理の結果を検証するテスト。
"""

from contextlib import closing

import pytest

import libs.global_value as g
from libs.commands.registry import member, team
from libs.utils import dbutil
from tests.database import param_data


def test_guest_name() -> None:
    """
    ゲストユーザ名の初期登録内容を検証する。

    member テーブルの id=0 レコードが設定値の guest_name と一致することを確認する。

    """
    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        cur = conn.execute("select name from member where id = 0;")
        row = dict(cur.fetchone())

    assert row is not None
    assert row.get("name") == g.cfg.member.guest_name


@pytest.mark.parametrize(
    "user_name, ret_meg, registered",
    list(param_data.user_add_case_01.values()),
    ids=list(param_data.user_add_case_01.keys()),
)
def test_member_add(user_name: str, ret_meg: str, registered: bool) -> None:
    """
    メンバー追加コマンドの結果とDB反映を検証する。

    応答メッセージ判定と member テーブルの登録有無の両方で期待値を確認する。

    """
    ret = member.append(str(user_name).split())
    print(ret)
    assert ret_meg in ret

    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        cur = conn.execute("select name from member;")
        rows = cur.fetchall()
        assert rows is not None

    check_name = user_name.split()[0]
    name_list = [dict(row).get("name") for row in rows]
    print(f"in: {check_name} result: {ret}")
    assert (check_name in name_list) == registered


@pytest.mark.parametrize(
    "team_name, ret_meg, registered",
    list(param_data.team_add_case_01.values()),
    ids=list(param_data.team_add_case_01.keys()),
)
def test_team_create(team_name: str, ret_meg: str, registered: bool) -> None:
    """
    チーム作成コマンドの結果とDB反映を検証する。

    返却メッセージと team テーブルの登録有無を照合して成功/失敗判定の整合性を確認する。
    """
    ret = team.create(str(team_name).split())
    assert ret_meg in ret

    with closing(dbutil.connection(g.cfg.setting.database_file)) as conn:
        cur = conn.execute("select name from team;")
        rows = cur.fetchall()
        assert rows is not None

    check_name = team_name.split()[0]
    name_list = [dict(row).get("name") for row in rows]
    print(f"in: {check_name} result: {ret}")
    assert (check_name in name_list) == registered
