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
from libs.functions.compose import text_item
from libs.types import CommandType
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


def header(game_info: "GameInfo", m: "MessageParserProtocol", add_text: str = "", indent: int = 1) -> str:
    """
    見出し生成

    Args:
        game_info (GameInfo): 集計範囲のゲーム情報
        m (MessageParserProtocol): メッセージデータ
        add_text (str, optional): 追加表示するテキスト. Defaults to "".
        indent (int, optional): 先頭のタブ数. Defaults to 1.

    Returns:
        str: 生成した見出し

    """
    text: list[str] = []
    assert isinstance(game_info.first_game, ExtDt)
    assert isinstance(game_info.last_game, ExtDt)

    # 対戦数
    if game_info.count == 0:
        text.extend(
            [
                f"検索範囲：{game_info.search_range}",
                f"\n{random_reply(m, 'no_hits')}",
            ]
        )
        return textwrap.indent("\n".join(text), "\t" * indent)

    # 検索範囲 / 集計範囲
    if g.params.command == "summary":
        text.extend(
            [
                f"検索範囲：{game_info.search_range}",
                f"最初のゲーム：{game_info.first_game.format(ExtDt.FMT.YMDHMS)}",
                f"最後のゲーム：{game_info.last_game.format(ExtDt.FMT.YMDHMS)}",
                f"集計対象：{game_info.count} ゲーム {add_text}".strip(),
            ]
        )
    else:
        text.extend(
            [
                f"検索範囲：{game_info.search_range}",
                f"集計対象：{game_info.count} ゲーム",
            ]
        )

    if remarks_text := remarks(deliverables=m.status.command_type, headword=True):
        text.append(f"{remarks_text}")
    if word_text := text_item.search_word(True):
        text.append(f"{word_text}")

    return textwrap.indent("\n".join(text), "\t" * indent)


def remarks(headword: bool = False, deliverables: Optional[CommandType] = None) -> str | list[str]:
    """
    引数で指定された集計方法を注記にまとめる

    Args:
        headword (bool, optional): 見出しを付ける. Defaults to False.
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
