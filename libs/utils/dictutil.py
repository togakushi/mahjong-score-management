"""
libs/utils/dictutil.py
"""

import logging
from typing import TYPE_CHECKING, Any, Protocol

import libs.global_value as g
from libs.domain.command import CommandParser
from libs.domain.placeholder import PlaceholderBuilder
from libs.functions import lookup, search
from libs.types import ChannelType
from libs.utils import formatter
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class SubCommandLike(Protocol):
    """placeholder生成に必要なサブコマンド設定の最小インターフェース"""

    section: str
    always_argument: list[str]
    aggregation_range: str

    def to_dict(self, drop_items: list[str] | None = None) -> dict[str, Any]: ...


def placeholder(subcom: "SubCommandLike", m: "MessageParserProtocol") -> PlaceholderBuilder:
    """
    プレースホルダに使用する辞書を生成

    Args:
        subcom (SubCommandLike): サブコマンド設定
        m (MessageParserProtocol): メッセージデータ

    Returns:
        PlaceholderBuilder: プレースホルダ用データ

    """
    # 初期化
    parser: CommandParser = CommandParser()
    params: PlaceholderBuilder = PlaceholderBuilder()
    rule_version: str | None = None
    params.update_from_dict(
        {
            "service_type": g.adapter.interface_type,
            "command": subcom.section,
            "guest_name": g.cfg.member.guest_name,
            "logging_verbose": g.args.verbose,
            **g.cfg.setting.to_dict(),
            **subcom.to_dict(),  #  サブコマンドデフォルト値
        }
    )

    # チャンネル個別設定読み込み
    if channel_config := g.cfg.read_channel_config(m.status.source, params.placeholder()):
        logging.debug("read channel config: %s", channel_config.absolute())
        params.channel_config = channel_config
        params.update_from_dict(subcom.to_dict())  # 更新

    # メンバー情報更新 # ToDo: DB切り替え実装後
    # g.cfg.member.guest_name = lookup.get_guest()
    # g.cfg.member.info = g.cfg.member.get_info
    # g.cfg.team.info = g.cfg.team.get_info

    params.source = g.cfg.resolve_channel_id(m.status.source)

    # セパレートフラグ更新
    params.update_setting(main_config=g.cfg.config_file, key_name="separate", val_type=bool)
    if m.data.channel_type in {ChannelType.DIRECT_MESSAGE, ChannelType.HOME_APP}:
        params.separate = False  # DM / HomeApp(slack) はセパレートしない

    # ルール識別子探索
    params.update_setting(main_config=g.cfg.config_file, key_name="default_rule", val_type=str)
    if (command_suffix := subcom.to_dict().get("command_suffix")) and isinstance(command_suffix, list):
        rule_version = lookup.get_current_rule_version(m, command_suffix)
    rule_version = rule_version if rule_version else params.default_rule
    params.update_from_dict(
        {
            **g.cfg.rule.to_dict(rule_version),
            "target_mode": g.cfg.rule.get_mode(rule_version),
        }
    )

    # always_argumentの処理
    pre_param = parser.analysis_argument(subcom.always_argument)
    logging.debug("analysis_argument: %s", pre_param)
    params.update_from_dict(pre_param.flags)

    # 引数の処理
    post_param = parser.analysis_argument(m.argument)
    logging.debug("argument: %s", post_param)
    params.update_from_dict(post_param.flags)  # 上書き

    # 検索範囲取得
    departure_time = ExtDt(hours=-g.cfg.setting.time_adjust)
    if post_param.search_range:
        search_range = post_param.search_range
    elif pre_param.search_range:
        search_range = pre_param.search_range
    else:
        search_range = departure_time.range(subcom.aggregation_range)

    params.starttime = (departure_time.range(search_range) + {"hours": g.cfg.setting.time_adjust}).start
    params.endtime = (departure_time.range(search_range) + {"hours": g.cfg.setting.time_adjust}).end
    params.onday = departure_time.range(search_range).end

    # どのオプションにも該当しないキーワード
    check_list: list[str] = post_param.unknown + pre_param.unknown

    # 追加ルール識別子
    rule_list: list[str] = []
    for name in list(check_list):
        if name in g.cfg.rule.keyword_mapping:  # マッピング済みルール識別子
            rule_list.append(g.cfg.rule.keyword_mapping.get(name, rule_version))
            check_list.remove(name)
        if name in g.cfg.rule.keyword_mapping.values():  # マッピング済みルール識別子
            rule_list.append(name)
            check_list.remove(name)
        if name in g.cfg.rule.rule_list:  # マッピングされていないルール識別子
            rule_list.append(name)
            if name in check_list:
                check_list.remove(name)
    if params.mixed:
        for rule in g.cfg.rule.rule_list:  # 全ルール追加
            if g.cfg.rule.get_mode(rule) == params.target_mode:
                rule_list.append(rule)
    if rule_list:
        params.rule_list.extend(list(set(rule_list)))
    else:
        params.rule_list.append(rule_version)

    # プレイヤー名
    target_player: list[str] = []
    if params.individual:
        if params.all_player:
            check_list.extend(g.cfg.member.lists)
        for name in check_list:
            if name in g.cfg.team.lists:  # チーム名がある場合は所属メンバーに展開
                target_player.extend(g.cfg.team.member(name))
            else:
                target_player.append(formatter.name_replace(name, not_replace=True))
    else:  # チーム名
        if params.all_player:
            check_list.extend(g.cfg.team.lists)
        for team in check_list:
            if team in g.cfg.member.lists:
                if team_name := g.cfg.team.which(team):  # プレイヤー名がある場合は所属チームを追加
                    target_player.append(team_name)
            else:
                target_player.append(team)

    target_player = sorted(set(target_player), key=target_player.index)  # 順序を維持したまま重複排除

    if target_player:
        params.player_name = target_player[0]
        params.target_player = target_player
        params.player_list = target_player
        params.competition_list = target_player[1:]

    # 出力タイプ
    if not params.format:
        params.format = "default"

    # 規定打数設定
    if params.mixed and not params.stipulated:  # 横断集計&規定数制限なし
        if target_player:
            params.stipulated = 1  # 個人成績
        else:
            params.stipulated = 0
    elif not params.stipulated:  # 通常集計&規定数制限なし
        if subcom.section == "ranking":  # ランキングはレート計算
            params.stipulated = 0
        else:
            params.stipulated = 1

    if departure_time.range(search_range).start == ExtDt("1900-01-01 00:00:00.000000"):
        params.starttime = search.first_record(
            g.cfg.rule.get_version(
                mode=params.mode,
                mapping=not (params.mixed),
            )
        )

    return params


def merge_dicts(dict1: dict[Any, Any], dict2: dict[Any, Any]) -> dict[Any, Any]:
    """
    辞書の内容をマージする

    Args:
        dict1 (dict[Any, Any]): 1つ目の辞書
        dict2 (dict[Any, Any]): 2つ目の辞書

    Returns:
        dict: マージされた辞書

    """
    merged: dict[Any, Any] = {}

    for key in set(dict1) | set(dict2):
        val1: Any = dict1.get(key)
        val2: Any = dict2.get(key)

        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            merged[key] = val1 + val2
        elif isinstance(val1, str) and isinstance(val2, str):
            merged[key] = val1 + val2
        elif isinstance(val1, list) and isinstance(val2, list):
            merged[key] = sorted(list(set(val1 + val2)))
        else:
            merged[key] = val1 if val2 is None else val2

    return merged
