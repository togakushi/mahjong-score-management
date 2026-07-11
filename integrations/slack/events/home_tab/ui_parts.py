"""
integrations/slack/events/home_tab/ui_parts.py
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

import libs.global_value as g
from libs.functions.lookup import read_memberslist

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from integrations.slack.adapter import ServiceAdapter


def plain_text(msg: str) -> dict[str, Any]:
    """
    プレーンテキストの埋め込み

    Args:
        msg (str): テキスト

    Returns:
        dict[str, Any]: ブロック要素

    """
    view: dict[str, Any] = {"type": "home", "blocks": []}
    view["blocks"].append({"type": "section", "text": {}})
    view["blocks"][0]["text"] = {"type": "mrkdwn", "text": msg}

    return view


def divider(adapter: "ServiceAdapter") -> None:
    """
    境界線を引く

    Args:
        adapter (ServiceAdapter): アダプタインターフェース

    """
    adapter.conf.tab_var["view"]["blocks"].append(
        {
            "type": "divider",
        }
    )
    adapter.conf.tab_var["no"] += 1


def header(adapter: "ServiceAdapter", text: str = "dummy") -> None:
    """
    ヘッダ生成

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        text (str, optional): ヘッダテキスト. Defaults to "dummy".

    """
    adapter.conf.tab_var["view"]["blocks"].append({"type": "header", "text": {}})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["text"] = {"type": "plain_text", "text": text}
    adapter.conf.tab_var["no"] += 1


def button(adapter: "ServiceAdapter", text: str, action_id: str, style: str | bool = False) -> None:
    """
    ボタン配置

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        text (str, optional): 表示テキスト
        action_id (str): action_id
        style (str | bool, optional): 表示スタイル. Defaults to False.

    """
    adapter.conf.tab_var["view"]["blocks"].append({"type": "actions", "elements": [{}]})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["elements"][0] = {
        "type": "button",
        "text": {},
        "action_id": action_id,
    }
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["elements"][0]["text"] = {
        "type": "plain_text",
        "text": text,
    }
    if style:
        adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["elements"][0].update({"style": style})

    adapter.conf.tab_var["no"] += 1


def radio_buttons(adapter: "ServiceAdapter", id_suffix: str, title: str, flag: dict[str, Any]) -> None:
    """
    オプション選択メニュー

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        id_suffix (str): block_id, action_id
        title (str): 表示タイトル
        flag (dict[str, Any]): 表示する選択項目

    """
    adapter.conf.tab_var["view"]["blocks"].append({"type": "input", "block_id": f"bid-{id_suffix}", "element": {}})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["label"] = {"type": "plain_text", "text": title}
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["type"] = "radio_buttons"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["action_id"] = f"aid-{id_suffix}"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["initial_option"] = {  # 先頭の選択肢はチェック済みにする
        "text": {"type": "plain_text", "text": flag[next(iter(flag))]},
        "value": next(iter(flag)),
    }
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"] = []
    for k, v in flag.items():
        adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"].append({"text": {"type": "plain_text", "text": v}, "value": k})
    adapter.conf.tab_var["no"] += 1


def checkboxes(
    adapter: "ServiceAdapter",
    id_suffix: str,
    title: str,
    flag: Optional[dict[str, Any]] = None,
    initial: Optional[list[str]] = None,
) -> None:
    """
    チェックボックス選択メニュー

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        id_suffix (str): block_id, action_id
        title (str): 表示タイトル
        flag (Optional[dict[str, Any]): 表示する選択項目. Defaults to None.
        initial (Optional[list[str]]): チェック済み項目. Defaults to None.

    """
    if flag is None:
        flag = {}

    adapter.conf.tab_var["view"]["blocks"].append({"type": "input", "block_id": f"bid-{id_suffix}", "element": {}})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["label"] = {"type": "plain_text", "text": title}
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["type"] = "checkboxes"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["action_id"] = f"aid-{id_suffix}"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"] = []
    if initial:
        adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["initial_options"] = []
    else:
        initial = []  # None -> list

    for k, v in flag.items():
        adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"].append({"text": {"type": "plain_text", "text": v}, "value": k})
        if k in initial:
            adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["initial_options"].append(
                {"text": {"type": "plain_text", "text": v}, "value": k}
            )

    adapter.conf.tab_var["no"] += 1


def user_select_pulldown(
    adapter: "ServiceAdapter",
    text: str = "dummy",
    add_list: Optional[list[str]] = None,
) -> None:
    """
    プレイヤー選択プルダウンメニュー

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        text (str, optional): 表示テキスト. Defaults to "dummy".
        add_list (Optional[list[str]]): プレイヤーリスト. Defaults to None.

    """
    read_memberslist()

    adapter.conf.tab_var["view"]["blocks"].append({"type": "input", "block_id": "bid-user_select", "element": {}})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["type"] = "static_select"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["action_id"] = "player"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["placeholder"] = {
        "type": "plain_text",
        "text": "Select an item",
    }
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"] = []

    if add_list:
        for val in add_list:
            adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"].append(
                {"text": {"type": "plain_text", "text": val}, "value": val}
            )

    for name in g.cfg.member.lists:
        adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"].append(
            {"text": {"type": "plain_text", "text": name}, "value": name}
        )

    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["label"] = {"type": "plain_text", "text": text}

    adapter.conf.tab_var["no"] += 1


def multi_select_pulldown(
    adapter: "ServiceAdapter",
    text: str = "dummy",
    add_list: Optional[list[str]] = None,
) -> None:
    """
    複数プレイヤー選択プルダウンメニュー

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        text (str, optional): 表示テキスト. Defaults to "dummy".
        add_list (Optional[list[str]]): プレイヤーリスト. Defaults to None.

    """
    read_memberslist()

    adapter.conf.tab_var["view"]["blocks"].append({"type": "input", "block_id": "bid-multi_select", "element": {}})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["type"] = "multi_static_select"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["action_id"] = "player"
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["placeholder"] = {
        "type": "plain_text",
        "text": "Select an item",
    }
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"] = []

    if add_list:
        for val in add_list:
            adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"].append(
                {"text": {"type": "plain_text", "text": val}, "value": val}
            )

    for name in g.cfg.member.lists:
        adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"]["options"].append(
            {"text": {"type": "plain_text", "text": name}, "value": name}
        )

    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["label"] = {"type": "plain_text", "text": text}

    adapter.conf.tab_var["no"] += 1


def input_ranked(adapter: "ServiceAdapter", block_id: str | bool = False) -> None:
    """
    ランキング上限入力テキストボックス

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        block_id (str | bool, optional): block_id. Defaults to False.

    """
    if block_id:
        adapter.conf.tab_var["view"]["blocks"].append({"type": "input", "block_id": block_id, "element": {}, "label": {}})
    else:
        adapter.conf.tab_var["view"]["blocks"].append({"type": "input", "element": {}, "label": {}})

    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"].update({"type": "number_input"})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"].update({"is_decimal_allowed": True})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"].update({"initial_value": str(g.cfg.analysis.ranked)})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"].update({"min_value": "1"})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["element"].update({"action_id": "aid-ranked"})
    adapter.conf.tab_var["view"]["blocks"][adapter.conf.tab_var["no"]]["label"].update({"type": "plain_text", "text": "出力順位上限"})

    adapter.conf.tab_var["no"] += 1


def modalperiod_selection(adapter: "ServiceAdapter") -> dict[str, Any]:
    """
    日付選択

    Args:
        adapter (ServiceAdapter): アダプタインターフェース

    Returns:
        dict[str, Any]: ブロック要素

    """
    view: dict[str, Any] = {"type": "modal", "callback_id": f"{adapter.conf.tab_var['screen']}_ModalPeriodSelection"}
    view["title"] = {"type": "plain_text", "text": "検索範囲指定"}
    view["submit"] = {"type": "plain_text", "text": "決定"}
    view["close"] = {"type": "plain_text", "text": "取消"}

    view["blocks"] = []
    view["blocks"].append({"type": "input", "element": {}, "label": {}})
    view["blocks"][0]["element"].update({"type": "datepicker"})
    view["blocks"][0]["element"].update({"initial_date": adapter.conf.tab_var["sday"]})
    view["blocks"][0]["element"].update({"placeholder": {"type": "plain_text", "text": "Select a date"}})
    view["blocks"][0]["element"].update({"action_id": "aid-sday"})
    view["blocks"][0]["label"].update({"type": "plain_text", "text": "開始日"})
    view["blocks"].append({"type": "input", "element": {}, "label": {}})
    view["blocks"][1]["element"].update({"type": "datepicker"})
    view["blocks"][1]["element"].update({"initial_date": adapter.conf.tab_var["eday"]})
    view["blocks"][1]["element"].update({"placeholder": {"type": "plain_text", "text": "Select a date"}})
    view["blocks"][1]["element"].update({"action_id": "aid-eday"})
    view["blocks"][1]["label"].update({"type": "plain_text", "text": "終了日"})

    return view


def set_command_option(
    adapter: "ServiceAdapter",
    body: dict[str, Any],
) -> tuple[list[str], list[str], dict[str, Any]]:
    """
    選択オプションの内容のフラグをセット

    Args:
        adapter (ServiceAdapter): アダプタインターフェース
        body (dict[str, Any]): イベント内容

    Returns:
        tuple[list[str], list[str], dict[str, Any]]:
        - list[str]: コマンドに追加する文字列
        - list[str]: viewに表示するメッセージ
        - dict[str, Any]: 変更されるフラグ

    """
    update_flag: dict[str, Any] = {}

    # 検索設定
    argument: list[str] = []
    search_options = body["view"]["state"]["values"]
    logging.debug("search options: %s", search_options)

    app_msg: list[str] = []
    adapter.conf.tab_var.update(operation=None)

    if "bid-user_select" in search_options:
        user_select = search_options["bid-user_select"]["player"]["selected_option"]
        if user_select is not None and "value" in user_select:
            player = str(user_select["value"])
            app_msg.append(f"対象プレイヤー：{player}")
            argument.append(player)

    if "bid-multi_select" in search_options:
        user_list = search_options["bid-multi_select"]["player"]["selected_options"]
        for _, val in enumerate(user_list):
            argument.append(str(val["value"]))

    if "bid-search_range" in search_options:
        match str(search_options["bid-search_range"]["aid-search_range"]["selected_option"]["value"]):
            case "指定":
                app_msg.append(f"集計範囲：{adapter.conf.tab_var['sday']} ～ {adapter.conf.tab_var['eday']}")
                argument.extend([str(adapter.conf.tab_var["sday"]), str(adapter.conf.tab_var["eday"])])
            case "全部":
                app_msg.append("集計範囲：全部")
                argument.append("全部")
            case _ as select_item:
                app_msg.append(f"集計範囲：{select_item}")
                argument.append(select_item)

    for id_suffix in ("search_option", "display_option", "output_option"):
        if f"bid-{id_suffix}" in search_options:
            match search_options[f"bid-{id_suffix}"][f"aid-{id_suffix}"].get("type"):
                case "checkboxes":
                    selected_options = search_options[f"bid-{id_suffix}"][f"aid-{id_suffix}"].get("selected_options")
                case "radio_buttons":
                    selected_options = [search_options[f"bid-{id_suffix}"][f"aid-{id_suffix}"].get("selected_option")]
                case _:
                    continue

            for _, val in enumerate(selected_options):
                match val["value"]:
                    case "unregistered_replace":
                        update_flag.update(unregistered_replace=False)
                    case "versus":
                        update_flag.update(versus=True)
                    case "game_results":
                        update_flag.update(game_results=True)
                    case "verbose":
                        update_flag.update(game_results=True)
                        update_flag.update(verbose=True)
                    case "comparisons":
                        update_flag.update(comparisons=True)
                        adapter.conf.tab_var.update(operation=None)
                    case _ as option:
                        adapter.conf.tab_var.update(operation=option)

    argument.append(g.cfg.rule.rule_list[0])

    app_msg.append("集計中…")
    return (argument, app_msg, update_flag)


def update_view(adapter: "ServiceAdapter", m: "MessageParserProtocol", msg: list[str]) -> None:
    """
    viewを更新する

    Args:
        adapter (ServiceAdapter): アダプター
        m (MessageParserProtocol): メッセージデータ
        msg (list[str]): 表示テキスト

    """
    text = ""
    if m.post.headline:
        header_data, header_option = m.post.headline
        if isinstance(header_data, str):
            text = f"\n【{header_option.title}】\n{header_data}"

    adapter.api.appclient.views_update(
        view_id=adapter.conf.tab_var["view_id"],
        view=plain_text(f"{chr(10).join(msg)}\n\n{text}".strip()),
    )
