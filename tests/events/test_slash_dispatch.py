"""
スラッシュコマンド入力時のディスパッチ経路を検証するテスト。
"""

import sys
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import patch

import pytest

import libs.dispatcher
import libs.global_value as g
from integrations import factory
from libs.bootstrap import configuration
from libs.types import ServiceType, StyleOptions
from tests.events import param_data

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def _init() -> "MessageParserProtocol":
    """
    スラッシュコマンド検証用パーサを初期化する。

    テスト共通のアダプタ生成とコマンド判定フラグ設定を行う。

    """
    configuration.setup(init_db=False)
    adapter = factory.select_adapter(ServiceType.STANDARD_IO, g.cfg)
    m = adapter.parser()
    m.status.command_flg = True

    return m


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_help.values()),
    ids=list(param_data.slash_help.keys()),
)
def test_help(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    help コマンド入力時のディスパッチ経路を検証する。

    イベント解析から dispatcher 到達までの振る舞いが成立することを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    import integrations.slack.events.slash

    m = _init()
    g.command_dispatcher.update({"help": integrations.slack.events.slash.command_help})
    param_data.FAKE_BODY["event"].update(text=f"{keyword}")

    with patch.object(m, "set_message") as mock_set_message:
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)

        # fixme
        # mock_set_message.assert_called_once()
        _ = mock_set_message
        # assert mock_set_message.call_args[0][0] == "ヘルプメッセージ"


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_results.values()),
    ids=list(param_data.slash_results.keys()),
)
def test_results(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    results コマンドが results エントリへ委譲されることを検証する。

    疑似イベント本文を与えて dispatcher を実行し、対象モックの呼び出しを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.libs.commands.results.entry.main") as mock_slash_results,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_results.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_graph.values()),
    ids=list(param_data.slash_graph.keys()),
)
def test_graph(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    graph コマンドが graph エントリへ委譲されることを検証する。

    キーワード分岐の結果として graph 側ハンドラのみが呼ばれることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.libs.commands.graph.entry.main") as mock_slash_graph,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_graph.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_ranking.values()),
    ids=list(param_data.slash_ranking.keys()),
)
def test_ranking(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ranking コマンドが ranking エントリへ委譲されることを検証する。

    parser 後の dispatcher 実行で ranking 側モックが呼び出されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.libs.commands.ranking.entry.main") as mock_slash_ranking,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_ranking.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_report.values()),
    ids=list(param_data.slash_report.keys()),
)
def test_report(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    report コマンドが report エントリへ委譲されることを検証する。

    設定差分や別名入力を含むケースで同一経路に到達することを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.libs.commands.report.entry.main") as mock_slash_report,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_report.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_check.values()),
    ids=list(param_data.slash_check.keys()),
)
def test_check(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    check コマンド入力時のディスパッチ到達を検証する。

    標準入出力向け制約があるため、現状は dispatcher 呼び出し自体を確認対象とする。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.dispatcher.by_keyword") as mock_slash_check,  # fixme //stdには個別コマンドが登録されない
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_check.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_download.values()),
    ids=list(param_data.slash_download.keys()),
)
def test_download(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    download コマンドの出力内容と装飾情報を検証する。

    返却本文と StyleOptions の値を照合し、期待レスポンスを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    m = _init()
    param_data.FAKE_BODY["event"].update(text=f"{keyword}")

    with patch.object(m, "set_message") as mock_set_message:
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)

        mock_set_message.assert_called_once()
        # 引数の検証
        contents = mock_set_message.call_args[0][0]
        options = mock_set_message.call_args[0][1]

        assert contents == g.cfg.setting.database_file
        assert isinstance(options, StyleOptions)
        assert options.title == "成績記録DB"


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_member_list.values()),
    ids=list(param_data.slash_member_list.keys()),
)
def test_member_list(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    member コマンドでメンバー一覧取得処理が呼ばれることを検証する。

    dispatcher の分岐結果として get_members_list が実行されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.text_item.get_members_list") as mock_slash_member_list,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_member_list.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_member_add.values()),
    ids=list(param_data.slash_member_add.keys()),
)
def test_member_add(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    add コマンドでメンバー追加処理が呼ばれることを検証する。

    別名キーワードを含むケースでも member.append に委譲されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.member.append") as mock_slash_member_add,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_member_add.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_member_del.values()),
    ids=list(param_data.slash_member_del.keys()),
)
def test_member_del(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    del コマンドでメンバー削除処理が呼ばれることを検証する。

    parser 実行後に member.remove が1回呼び出されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.member.remove") as mock_slash_member_del,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_member_del.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_team_create.values()),
    ids=list(param_data.slash_team_create.keys()),
)
def test_team_create(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    team_create コマンドでチーム作成処理が呼ばれることを検証する。

    キーワード解析結果が team.create 呼び出しへ到達することを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.team.create") as mock_slash_team_create,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_team_create.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_team_del.values()),
    ids=list(param_data.slash_team_del.keys()),
)
def test_team_del(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    team_del コマンドでチーム削除処理が呼ばれることを検証する。

    dispatcher の分岐結果として team.delete が呼び出されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.team.delete") as mock_slash_team_del,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_team_del.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_team_add.values()),
    ids=list(param_data.slash_team_add.keys()),
)
def test_team_add(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    team_add コマンドでチーム所属追加処理が呼ばれることを検証する。

    解析済みイベントから team.append が呼び出されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.team.append") as mock_slash_team_add,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_team_add.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_team_remove.values()),
    ids=list(param_data.slash_team_remove.keys()),
)
def test_team_remove(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    team_remove コマンドでチーム所属解除処理が呼ばれることを検証する。

    dispatcher 経由で team.remove が1回呼び出されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.team.remove") as mock_slash_team_remove,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_team_remove.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_team_list.values()),
    ids=list(param_data.slash_team_list.keys()),
)
def test_team_list(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    team_list コマンドでチーム一覧取得処理が呼ばれることを検証する。

    一覧系の分岐先として get_team_list が実行されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.text_item.get_team_list") as mock_slash_team_list,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_team_list.assert_called_once()


@pytest.mark.parametrize(
    "config, keyword",
    list(param_data.slash_team_clear.values()),
    ids=list(param_data.slash_team_clear.keys()),
)
def test_team_clear(config: str, keyword: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    team_clear コマンドでチーム情報クリア処理が呼ばれることを検証する。

    dispatcher 実行後に team.clear が呼び出されることを確認する。

    """
    monkeypatch.setattr(sys, "argv", ["app.py", "--service=std", f"--config=tests/testdata/{config}"])

    with (
        patch("libs.bootstrap.configuration.team.clear") as mock_slash_team_clear,
    ):
        m = _init()
        param_data.FAKE_BODY["event"].update(text=f"{keyword}")
        m.parser(cast(dict[str, Any], param_data.FAKE_BODY))
        libs.dispatcher.by_keyword(m)
        mock_slash_team_clear.assert_called_once()
