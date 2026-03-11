"""
integrations/slack/events/home_tab/home.py
"""

import logging
from typing import TYPE_CHECKING, Any

from integrations.slack.adapter import ServiceAdapter
from integrations.slack.events.handler_registry import register
from integrations.slack.events.home_tab import ui_parts

if TYPE_CHECKING:
    from slack_bolt import App


def build_main_menu(adapter: ServiceAdapter) -> None:
    """
    メインメニューを生成する

    Args:
        adapter (ServiceAdapter): インターフェースアダプタ

    """
    adapter.conf.tab_var["screen"] = "MainMenu"
    adapter.conf.tab_var["no"] = 0
    adapter.conf.tab_var["view"] = {"type": "home", "blocks": []}
    ui_parts.button(adapter, text="成績サマリ", action_id="summary_menu")
    ui_parts.button(adapter, text="ランキング", action_id="ranking_menu")
    ui_parts.button(adapter, text="個人成績", action_id="personal_menu")
    ui_parts.button(adapter, text="直接対戦", action_id="versus_menu")


@register
def register_home_handlers(app: "App", adapter: ServiceAdapter) -> None:
    """ホームタブ操作イベント"""

    @app.action("actionId-back")
    def handle_action(ack: Any, body: Any) -> None:
        """
        戻るボタン

        Args:
            ack (Any): ack
            body (Any): イベント内容

        """
        ack()
        logging.trace(body)  # type: ignore

        build_main_menu(adapter)
        adapter.api.appclient.views_publish(
            user_id=adapter.conf.tab_var["user_id"],
            view=adapter.conf.tab_var["view"],
        )

    @app.action("modal-open-period")
    def handle_open_modal_button_clicks(ack: Any, body: Any) -> None:
        """
        検索範囲設定選択イベント

        Args:
            ack (Any): ack
            body (Any): イベント内容

        """
        ack()

        adapter.api.appclient.views_open(
            trigger_id=body["trigger_id"],
            view=ui_parts.modalperiod_selection(adapter),
        )
