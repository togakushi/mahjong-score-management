"""
libs/functions/message.py
"""

import logging
import random
import textwrap
from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import libs.global_value as g
from libs.functions import badge
from libs.types import CommandType
from libs.utils import textutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.domain.datamodels import GameInfo


def random_reply(m: "MessageParserProtocol", message_type: str) -> str:
    """
    メッセージをランダムに返す

    Args:
        m (MessageParserProtocol): メッセージデータ
        message_type (str): 応答メッセージの種類

    Returns:
        str: 応答メッセージ

    """
    parser = ConfigParser()
    parser.read(g.cfg.config_file, encoding="utf-8")

    correct_score = g.params.origin_point * 4  # 配給原点
    rpoint_diff = abs(correct_score - m.status.rpoint_sum)

    default_message_type = {
        "invalid_argument": "使い方が間違っています。",
        "no_hits": "{start} ～ {end} に成績記録キーワードが見つかりません。",
        "no_target": "集計対象データがありません。",
        "invalid_score": "素点合計：{rpoint_sum}\n点数差分：{rpoint_diff}",
        "restricted_channel": "<@{user_id}> この投稿はデータベースに反映されません。",
        "inside_thread": "<@{user_id}> スレッド内から成績登録はできません。",
        "same_player": "同名のプレイヤーがいます。",
        "not_implemented": "未実装",
        "access_denied": "アクセスが拒否されました。",
        "rule_mismatch": "集計モード(四人打/三人打)の指定と集計対象ルールに矛盾があります。",
    }

    msg = default_message_type.get(message_type, "invalid_argument")

    if g.cfg.main_parser.has_section(m.status.source):
        if channel_config := g.cfg.main_parser[m.status.source].get("channel_config"):
            parser.read(Path(channel_config), encoding="utf-8")

    if parser.has_section("custom_message"):
        msg_list = []
        for key, val in parser.items("custom_message"):
            if key.startswith(message_type):
                msg_list.append(val)
        if msg_list:
            msg = random.choice(msg_list)

    if keywords := g.cfg.rule.keywords(g.params.rule_version):
        keyword = list(keywords)[0]
    else:
        keyword = list(g.cfg.rule.keyword_mapping.keys())[0]

    try:
        msg = str(
            # 文字列置き換え
            msg.format(
                user_id=m.data.user_id,
                keyword=keyword,
                start=ExtDt(g.params.starttime).format(ExtDt.FMT.YMD),
                end=ExtDt(g.params.onday).format(ExtDt.FMT.YMD),
                rpoint_diff=rpoint_diff * 100,
                rpoint_sum=m.status.rpoint_sum * 100,
            )
        )
    except KeyError as err:
        logging.warning("[unknown keywords] %s: %s", err, msg)
        msg = msg.replace("{user_id}", m.data.user_id)

    return msg


def search_word(headword: bool = False) -> str:
    """
    キーワード検索条件を返す

    Args:
        headword (bool, optional): 見出しを付ける。 Defaults to False.

    Returns:
        str: 条件をまとめた文字列

    """
    if ret := g.params.search_word.replace("%", ""):
        # 集約条件
        if g.params.group_length:
            ret += f"（{g.params.group_length}文字集約）"
    else:
        ret = ""

    if headword:
        if ret:
            return f"検索ワード：{ret}"

    return ret


def header(game_info: "GameInfo", m: "MessageParserProtocol", add_text: str = "", indent: int = 1) -> str:
    """
    見出し生成

    Args:
        game_info (GameInfo): 集計範囲のゲーム情報
        m (MessageParserProtocol): メッセージデータ
        add_text (str, optional): 追加表示するテキスト。 Defaults to "".
        indent (int, optional): 先頭のタブ数。 Defaults to 1.

    Returns:
        str: 生成した見出し

    """
    assert isinstance(game_info.first_game, ExtDt)
    assert isinstance(game_info.last_game, ExtDt)

    def _check_game_count() -> bool:
        """
        対戦数チェック

        Returns:
            bool: 集計対象がない場合は ``False`` を返す

        """

        if game_info.count:
            return True
        else:
            # 集計対象データが0件の場合
            if g.params.individual:  # 個人集計
                pass
            else:  # チーム集計
                if g.params.player_name not in g.cfg.team.lists:
                    text.append("\n登録されていないチームです。")
                    return False

            if m.status.command_type == CommandType.RECORD_DATA:
                text.append(f"対戦数：0 戦 (0 勝 0 敗 0 分) {badge.status(0, 0)}")
                if g.params.individual:
                    text.append(f"\n{random_reply(m, 'no_target')}")
                else:
                    text.append(f"\n{random_reply(m, 'no_target')}")
            else:
                text.append(f"\n{random_reply(m, 'no_hits')}")

        return False

    text: list[str] = []

    # 検索条件
    if m.status.command_type == CommandType.RECORD_DATA:  # 成績詳細ヘッダ
        if g.params.individual:
            text.append(
                "プレイヤー名：{player_name} {badge_degree}".format(
                    player_name=textutil.name_replace(g.params.player_name, add_mark=True),
                    badge_degree=badge.degree(game_info.stats.seat0.count),
                ).strip()
            )
            if team_name := g.cfg.team.which(g.params.player_name):
                text.append(f"所属チーム：{team_name}")
        else:
            text.append(
                "チーム名：{team_name} {badge_degree}".format(
                    team_name=g.params.player_name,
                    badge_degree=badge.degree(game_info.stats.seat0.count),
                ).strip()
            )
            if member_list := g.cfg.team.member(g.params.player_name):
                text.append(f"所属メンバー：{'、'.join(member_list)}")

    text.append(f"検索範囲：{game_info.search_range}")
    if word_text := search_word(True):
        text.append(f"{word_text}")

    # 対戦数チェック
    if not _check_game_count():
        return textwrap.indent("\n".join(text), "\t" * indent)

    # 集計範囲
    if g.params.command == "summary":
        match m.status.command_type:
            case CommandType.RECORD_DATA:  # 成績詳細ヘッダ
                text.append(f"集計範囲：{game_info.aggregation_range}")
            case CommandType.GAME_RESULTS:  # 連続戦集計
                if g.params.chain > 1:
                    if g.params.reverse:
                        text.append(f"集計条件：連続{g.params.chain}ゲーム / ワースト{g.params.ranked}")
                    else:
                        text.append(f"集計条件：連続{g.params.chain}ゲーム / ベスト{g.params.ranked}")
            case _:
                text.extend(
                    [
                        f"最初のゲーム：{game_info.first_game.format(ExtDt.FMT.YMDHMS)}",
                        f"最後のゲーム：{game_info.last_game.format(ExtDt.FMT.YMDHMS)}",
                        f"集計対象：{game_info.count} ゲーム {add_text}".strip(),
                    ]
                )
    else:
        text.append(f"集計対象：{game_info.count} ゲーム")

    if remarks_text := remarks(deliverables=m.status.command_type, headword=True):
        text.append(f"{remarks_text}")
    if word_text := search_word(True):
        text.append(f"{word_text}")

    return textwrap.indent("\n".join(text), "\t" * indent)


def remarks(headword: bool = False, deliverables: Optional[CommandType] = None) -> str | list[str]:
    """
    引数で指定された集計方法を注記にまとめる

    Args:
        headword (bool, optional): 見出しを付ける。 Defaults to False.
        deliverables (CommandType, optional): コマンドタイプ

    Returns:
        Union[list, str]:

        - ``headword`` がない場合はリストで返す
        - ``headword`` がある場合は文字列で返す

    """
    remark_list: list[str] = []

    if deliverables == CommandType.GAME_STATISTICS:
        if not g.params.unregistered_replace or not g.params.guest_skip:
            remark_list.append("2ゲスト戦の結果を含む")
    else:
        if g.params.individual:  # 個人集計時のみ表示
            if not g.params.unregistered_replace:
                remark_list.append("ゲスト置換なし(" + g.cfg.setting.guest_mark + "：未登録プレイヤー)")
            if not g.params.guest_skip:
                remark_list.append("2ゲスト戦の結果を含む")
        else:  # チーム集計時
            if g.params.friendly_fire:
                if g.params.game_results and g.params.verbose:
                    remark_list.append("チーム同卓時の結果を含む(" + g.cfg.setting.guest_mark + ")")
                else:
                    remark_list.append("チーム同卓時の結果を含む")

        if g.params.stipulated >= 2:
            remark_list.append(f"規定打数 {g.params.stipulated}G以上")
        if deliverables in [CommandType.RANKING, CommandType.RATING]:
            remark_list.append(f"{g.params.ranked}位まで表示")

    # 集計ルール
    if g.params.mixed:
        match g.params.target_mode:
            case 3:
                remark_list.append("集計対象ルール すべて(三人打)")
            case 4:
                remark_list.append("集計対象ルール すべて(四人打)")
            case _:
                remark_list.append("集計対象ルール すべて")
    elif len(g.params.rule_list) > 1:
        remark_list.append(f"集計対象ルール {'、'.join(g.params.rule_list)}")
    elif g.params.rule_version != g.params.default_rule:
        remark_list.append(f"集計対象ルール {'、'.join(g.params.rule_list)}")

    if headword:
        if remark_list:
            return f"特記事項：{'、'.join(remark_list)}"
        return "特記事項：なし"

    return remark_list
