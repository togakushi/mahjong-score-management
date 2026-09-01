"""
libs/utils/dictutil.py
"""

import logging
from typing import TYPE_CHECKING, Any, Optional, cast

import libs.global_value as g
from libs.domain.command import CommandParser
from libs.domain.placeholder import PlaceholderBuilder
from libs.domain.section import CommandClassType
from libs.functions import lookup
from libs.types import ChannelType, StyleOptions
from libs.utils import textutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def placeholder(subcom: CommandClassType, m: "MessageParserProtocol") -> PlaceholderBuilder:
    """
    プレースホルダに使用する辞書を生成

    Args:
        subcom (CommandClassType): コマンド設定
        m (MessageParserProtocol): メッセージデータ

    Returns:
        PlaceholderBuilder: プレースホルダ用データ

    """
    # 初期化
    g.cfg.initialization()
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
            **subcom.to_dict(),  #  コマンドデフォルト値
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
    params.update_setting(main_config=g.cfg.config_file, key_name="default_rule", val_type=str, fallback="default_rule")
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
                target_player.append(textutil.name_replace(name, guest_replace=False))
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
        if subcom.section == "analysis":  # 分析はレート計算
            params.stipulated = 0
        else:
            params.stipulated = 1

    if departure_time.range(search_range).start == ExtDt("1900-01-01 00:00:00.000000"):
        params.starttime = lookup.first_record(
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
        elif isinstance(val1, list) and isinstance(val2, list):
            merged[key] = sorted(list(set(val1 + val2)))
        else:
            merged[key] = val1 if val2 is None else val2

    return merged


def rename_dicts(columns: list[str], options: StyleOptions = StyleOptions()) -> dict[str, str]:
    """
    カラムリネーム用辞書の生成

    Args:
        columns (list[str]): カラム名
        options (StyleOptions): 変換モード

    Returns:
        dict[str,str]: リネーム用辞書

    """
    rename_dict: dict[str, str] = {
        #
        "p1": "東家",
        "p2": "南家",
        "p3": "西家",
        "p4": "北家",
        "alias": "別名",
        "members": "所属メンバー",
        "last_update": "最終更新日",
        "elapsed_day": "経過日数",
        #
        "playtime": "日時",
        "rate": "レート",
        "participation_rate": "ゲーム参加率",
        "total_count": "集計対戦数",
        "matter_count": "回数",
        "ex_total": "ポイント合計",
        "deposit": "供託",
        "comment": "コメント",
        "source": "入力元",
        "rule_version": "ルール識別子",
        "war_record": "戦績(勝-敗-分)",
        #
        "rpoint": "素点",
        "rpoint_avg": "平均素点",
        "balance_avg": "平均収支",
        "point_dev": "得点偏差",
        "rank_dev": "順位偏差",
        "grade": "段位",
        "pt_diff": "差分",
        "diff_from_above": "順位差",
        "diff_from_top": "トップ差",
        "consecutive_record": "獲得ポイント",
        "acquisition_rank": "獲得順位",
        "total_game": "総対戦数",
        "end_time": f"{g.params.chain}戦目",
        #
        "rank1_rate-count": "1位率(回)",
        "rank1_rate": "1位率",
        "rank1.5_rate-count": "1.5位率(回)",
        "rank1.5_rate": "1.5位率",
        "rank2_rate-count": "2位率(回)",
        "rank2_rate": "2位率",
        "rank2.5_rate-count": "2.5位率(回)",
        "rank2.5_rate": "2.5位率",
        "rank3_rate-count": "3位率(回)",
        "rank3_rate": "3位率",
        "rank3.5_rate-count": "3.5位率(回)",
        "rank3.5_rate": "3.5位率",
        "rank4_rate-count": "4位率(回)",
        "rank4_rate": "4位率",
        "top2_rate-count": "連対率(回)",
        "top2_rate": "連対率",
        "top2": "連対数",
        "top3_rate-count": "ラス回避率(回)",
        "top3_rate": "ラス回避率",
        "top3": "ラス回避数",
        "flying_rate-count": "トビ率(回)",
        "flying_rate": "トビ率",
        "flying_count": "トビ数",
        "yakuman_rate-count": "役満和了率(回)",
        "yakuman_rate": "役満和了率",
        # 収支
        "avg_balance": "平均収支",
        "top2_balance": "連対収支",
        "lose2_balance": "逆連対収支",
        "rank1_balance": "1位収支",
        "rank2_balance": "2位収支",
        "rank3_balance": "3位収支",
        "rank4_balance": "4位収支",
        # 素点分析
        "rank1_avg_diff": "1位偏差",
        "rank2_avg_diff": "2位偏差",
        "rank3_avg_diff": "3位偏差",
        "rank4_avg_diff": "4位偏差",
        # レコード
        "top1_max": "連続トップ",
        "top2_max": "連続連対",
        "top3_max": "連続ラス回避",
        "lose2_max": "連続トップなし",
        "lose3_max": "連続逆連対",
        "lose4_max": "連続ラス",
        "point_max": "最大獲得ポイント",
        "point_min": "最小獲得ポイント",
        "rpoint_max": "最大素点",
        "rpoint_min": "最小素点",
        # 直接対決
        "results": "対戦結果",
        "win%": "勝率",
        "my_point_sum": "獲得ポイント(自分)",
        "my_point_avg": "平均ポイント(自分)",
        "vs_point_sum": "獲得ポイント(相手)",
        "vs_point_avg": "平均ポイント(相手)",
        "my_rpoint_avg": "平均素点(自分)",
        "my_rank_avg": "平均順位(自分)",
        "my_rank_distr": "順位分布(自分)",
        "vs_rpoint_avg": "平均素点(相手)",
        "vs_rank_avg": "平均順位(相手)",
        "vs_rank_distr": "順位分布(相手)",
        #
        "evaluation": "評価点",
        #
        "p1_name": "東家 名前",
        "p2_name": "南家 名前",
        "p3_name": "西家 名前",
        "p4_name": "北家 名前",
        "p1_yakuman": "東家 メモ",
        "p2_yakuman": "南家 メモ",
        "p3_yakuman": "西家 メモ",
        "p4_yakuman": "北家 メモ",
        "p1_remarks": "東家 メモ",
        "p2_remarks": "南家 メモ",
        "p3_remarks": "西家 メモ",
        "p4_remarks": "北家 メモ",
        "p1_rpoint": "東家 素点",
        "p2_rpoint": "南家 素点",
        "p3_rpoint": "西家 素点",
        "p4_rpoint": "北家 素点",
        "p1_rank": "東家 順位",
        "p2_rank": "南家 順位",
        "p3_rank": "西家 順位",
        "p4_rank": "北家 順位",
        "p1_point": "東家 ポイント",
        "p2_point": "南家 ポイント",
        "p3_point": "西家 ポイント",
        "p4_point": "北家 ポイント",
        "p1_str": "東家 入力素点",
        "p2_str": "南家 入力素点",
        "p3_str": "西家 入力素点",
        "p4_str": "北家 入力素点",
        # レポート - 上位成績
        "collection": "集計月",
        "name1": "1位(名前)",
        "point1": "1位(ポイント)",
        "name2": "2位(名前)",
        "point2": "2位(ポイント)",
        "name3": "3位(名前)",
        "point3": "3位(ポイント)",
        "name4": "4位(名前)",
        "point4": "4位(ポイント)",
        "name5": "5位(名前)",
        "point5": "5位(ポイント)",
        # メモ
        "regulation": "卓外清算",
        "remarks": "メモ",
        #
        "memo": "備考",
    }

    match options.rename_type:
        case StyleOptions.RenameType.NONE:
            return {x: x for x in columns}
        case StyleOptions.RenameType.NORMAL:
            short = False
        case StyleOptions.RenameType.SHORT:
            short = True

    for x in columns:
        match x:
            case "rank":
                rename_dict[x] = "#" if short else "順位"
            case "name" | "player":
                rename_dict[x] = "名前" if short else "プレイヤー名"
            case "team":
                rename_dict[x] = "チーム" if short else "チーム名"
            case "point":
                rename_dict[x] = "ポイント" if short else "獲得ポイント"
            case "seat":
                rename_dict[x] = "席" if short else "座席"
            case "count" | "game" | "game_count":
                rename_dict[x] = "対戦数"
            case "pt_total" | "total_point" | "point_sum" | "total_mix":
                rename_dict[x] = "通算" if short else "通算ポイント"
            case "pt_avg" | "avg_point" | "point_avg" | "avg_mix":
                rename_dict[x] = "平均" if short else "平均ポイント"
            case "ex_point":
                rename_dict[x] = "ポイント" if short else "卓外ポイント"
            case "rank_distr" | "rank_distr1" | "rank_distr2" | "rank_distr3" | "rank_distr4":
                rename_dict[x] = "順位分布"
            case "rank_avg":
                rename_dict[x] = "平順" if short else "平均順位"
            case "rank1" | "rank1_count":
                rename_dict[x] = "1位数"
            case "rank1.5" | "rank1.5_count":
                rename_dict[x] = "1.5位数"
            case "rank2" | "rank2_count":
                rename_dict[x] = "2位数"
            case "rank2.5" | "rank2.5_count":
                rename_dict[x] = "2.5位数"
            case "rank3" | "rank3_count":
                rename_dict[x] = "3位数"
            case "rank3.5" | "rank3.5_count":
                rename_dict[x] = "3.5位数"
            case "rank4" | "rank4_count":
                rename_dict[x] = "4位数"
            case "flying":
                rename_dict[x] = "飛" if short else "トビ"
            case "yakuman_count" | "yakuman":
                rename_dict[x] = "役満和了数"
            case "win":
                rename_dict[x] = "勝" if short else "勝ち"
            case "lose":
                rename_dict[x] = "負" if short else "負け"
            case "draw":
                rename_dict[x] = "分" if short else "引き分け"
            case "matter":
                match options.data_kind:
                    case StyleOptions.DataKind.REMARKS_YAKUMAN:
                        rename_dict[x] = "和了役"
                    case StyleOptions.DataKind.REMARKS_REGULATION | StyleOptions.DataKind.REMARKS_OTHER:
                        rename_dict[x] = "内容"
                    case _:
                        rename_dict[x] = "内容"
            case "rolling_point":
                if g.params.chain == 1:
                    rename_dict[x] = "獲得ポイント"
                else:
                    rename_dict[x] = "合計ポイント"
            case "start_time":
                if g.params.chain == 1:
                    rename_dict[x] = "対戦日時"
                else:
                    rename_dict[x] = "1戦目"

    if not g.params.individual:
        rename_dict.update(name="チーム" if short else "チーム名")

    return rename_dict


def dropitems_list(item_list: Optional[list[str]] = None) -> list[str]:
    """
    非表示項目を集合で返す

    Args:
        item_list (Optional[list[str]]): 表示項目リスト

    Returns:
        list[str]: 非表示項目のリスト

    """
    if not item_list:
        item_list = []

    hide_items = g.cfg.rule.dropitems(g.params.rule_version)
    if g.params.command in ["summary", "analysis"]:
        hide_items = hide_items.union(set(cast(CommandClassType, getattr(g.cfg, g.params.command)).dropitems))

    if g.params.ignore_flying:
        hide_items.add("トビ")
    if not g.cfg.rule.remarks_words:
        hide_items.add("メモ")

    # 関連ワードを追加
    related_words_set: dict[str, set[str]] = {
        "flying": {"トビ", "トビ率", "飛", "flying", "flying_count", "flying_rate", "flying_rate-count"},
        "yakuman": {"役満", "役満和了", "役満和了率", "yakuman_count", "yakuman_rate", "yakuman_rate-count"},
        "regulation": {"卓外", "卓外清算", "卓外ポイント"},
        "other": {"その他", "メモ"},
    }
    for words_set in related_words_set.values():
        if hide_items & words_set:
            hide_items = hide_items.union(words_set)

    rename_dict = rename_dicts(
        item_list,
        StyleOptions(rename_type=StyleOptions.RenameType.NORMAL),
    )
    for k, v in rename_dict.items():
        if set([k, v]) & hide_items:
            hide_items = hide_items.union({k, v})

    rename_dict_short = rename_dicts(
        item_list,
        StyleOptions(rename_type=StyleOptions.RenameType.SHORT),
    )
    for k, v in rename_dict_short.items():
        if set([k, v]) & hide_items:
            hide_items = hide_items.union({k, v})

    if item_list:
        return list(hide_items & set(item_list))
    else:
        return list(hide_items)
