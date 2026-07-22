"""
Web統合ルートの公開範囲と認証動作を検証するテスト。
"""

import os
import sys
from typing import Any, cast
from unittest.mock import patch

import pytest
from flask import Flask, testing
from flask_httpauth import HTTPBasicAuth  # type: ignore

import libs.global_value as g
from integrations import factory
from integrations.web.events import create_bp
from libs.bootstrap import configuration
from libs.types import ServiceType


@pytest.fixture(scope="module", autouse=True)
def patch_by_keyword() -> Any:
    """
    Web統合テスト全体で by_keyword をモック化する。

    ルーティング検証に集中するため、内部コマンド実行の副作用を抑止する。

    Args:
        None.

    Returns:
        Any: モック化された by_keyword オブジェクト。

    """
    with patch("libs.dispatcher.by_keyword") as mock_by_keyword:
        mock_by_keyword.return_value = None
        yield mock_by_keyword


@pytest.fixture(name="flask_client")
def client(request: pytest.FixtureRequest) -> Any:
    """
    設定別に初期化済みの Flask テストクライアントを生成する。

    Blueprint と認証フックを含む構成をテスト環境へ組み立てて提供する。

    Args:
        request (pytest.FixtureRequest): 間接パラメータで渡される設定ファイル名を含むフィクスチャ要求。

    Returns:
        Any: 初期化済みの Flask テストクライアント。

    """
    config_path = request.param
    sys.argv = ["app.py", "--service=web", f"--config=tests/test_data/{config_path}"]
    configuration.setup(init_db=False)

    adapter = factory.select_adapter(ServiceType.WEB, g.cfg)

    app = Flask(
        __name__,
        static_folder=os.path.join(g.cfg.script_dir, "files/html/static"),
        template_folder=os.path.join(g.cfg.script_dir, "files/html/template"),
    )

    app.config["TESTING"] = True
    app.config["padding"] = "0.25em 1.5em"
    app.config["summary"] = ""
    app.config["analysis"] = ""
    app.config["players"] = []
    app.register_blueprint(create_bp.index_bp(adapter))
    app.register_blueprint(create_bp.summary_bp(adapter))
    app.register_blueprint(create_bp.graph_bp(adapter))
    app.register_blueprint(create_bp.ranking_bp(adapter))
    app.register_blueprint(create_bp.detail_bp(adapter))
    app.register_blueprint(create_bp.report_bp(adapter))
    app.register_blueprint(create_bp.member_bp(adapter))
    app.register_blueprint(create_bp.score_bp(adapter))
    app.register_blueprint(create_bp.user_assets_bp(adapter))

    auth = HTTPBasicAuth()

    @auth.verify_password  # type: ignore[untyped-decorator]
    def verify_password(username: str, password: str) -> bool:
        if username == adapter.conf.username and password == adapter.conf.password:
            return True
        return False

    @app.before_request
    def require_auth() -> Any:
        if adapter.conf.require_auth:
            return auth.login_required(lambda: None)()
        return None

    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize(
    "flask_client, url, expected_status",
    [
        ("empty.ini", "/", 200),
        ("empty.ini", "/summary/", 200),
        ("empty.ini", "/graph/", 200),
        ("empty.ini", "/ranking/", 200),
        ("empty.ini", "/detail/", 200),
        ("empty.ini", "/report/", 200),
        ("empty.ini", "/score/", 403),
        ("empty.ini", "/member/", 403),
        ("empty.ini", "/unknown/", 404),
        ("empty.ini", "/static/stylesheet.css", 200),
        ("empty.ini", "/static/unknown.css", 404),
        ("empty.ini", "/user_static/user.css", 403),
        ("empty.ini", "/user_static/config.ini", 403),
        ("web_customize.ini", "/", 200),
        ("web_customize.ini", "/summary/", 403),
        ("web_customize.ini", "/graph/", 403),
        ("web_customize.ini", "/ranking/", 403),
        ("web_customize.ini", "/detail/", 403),
        ("web_customize.ini", "/report/", 200),
        ("web_customize.ini", "/member/", 200),
        ("web_customize.ini", "/score/", 200),
        ("web_customize.ini", "/static/stylesheet.css", 200),
        ("web_customize.ini", "/static/unknown.css", 404),
        ("web_customize.ini", "/user_static/user.css", 200),
        ("web_customize.ini", "/user_static/config.ini", 403),
        ("web_with_auth.ini", "/", 401),
        ("web_with_auth.ini", "/summary/", 401),
        ("web_with_auth.ini", "/graph/", 401),
        ("web_with_auth.ini", "/ranking/", 401),
        ("web_with_auth.ini", "/detail/", 401),
        ("web_with_auth.ini", "/report/", 401),
        ("web_with_auth.ini", "/member/", 401),
        ("web_with_auth.ini", "/score/", 401),
        ("web_with_auth.ini", "/static/stylesheet.css", 401),
        ("web_with_auth.ini", "/static/unknown.css", 401),
        ("web_with_auth.ini", "/user_static/user.css", 401),
        ("web_with_auth.ini", "/user_static/config.ini", 401),
    ],
    indirect=["flask_client"],
)
def test_route_access(flask_client: str, url: str, expected_status: int) -> None:
    """
    URLごとのアクセス結果ステータスを検証する。

    設定パターン別の公開/制限ルート判定が期待どおりかを確認する。

    Args:
        flask_client (str): indirect フィクスチャで提供されるテストクライアント。
        url (str): 検証対象のリクエストパス。
        expected_status (int): 期待するHTTPステータスコード。

    """
    print("-->", url)

    response = cast(testing.FlaskClient, flask_client).get(url)
    assert response.status_code == expected_status
