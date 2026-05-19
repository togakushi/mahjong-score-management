"""
libs/utils/formatter.py
"""

import random
import re
from typing import Optional, cast

import libs.global_value as g
from libs.bootstrap.section import SubCommands
from libs.types import StyleOptions
from libs.utils import dictutil, textutil


def name_replace(target: str, add_mark: bool = False, not_replace: bool = False) -> str:
    """
    表記ブレ修正(正規化)

    Args:
        target (str): 対象プレイヤー名
        add_mark (bool, optional): ゲストマークを付与する. Defaults to False.
        not_replace (bool, optional): ゲスト置換なし(強制/個人戦) Defaults to False.

            - *True*: ゲストを置換しない
            - *False*: ゲストを置換する

    Returns:
        str: 表記ブレ修正後のプレイヤー名

    """
    chk_pattern = [
        target,  # 無加工
        textutil.str_conv(target, textutil.ConversionType.HtoZ),  # 半角 -> 全角
        textutil.str_conv(target, textutil.ConversionType.KtoH),  # カタ -> ひら
        textutil.str_conv(target, textutil.ConversionType.HtoK),  # ひら -> カタ
        honor_remove(target),  # 敬称削除
        honor_remove(textutil.str_conv(target, textutil.ConversionType.HtoZ)),  # 敬称削除 + 半角 -> 全角
        honor_remove(textutil.str_conv(target, textutil.ConversionType.KtoH)),  # 敬称削除 + カタ -> ひら
        honor_remove(textutil.str_conv(target, textutil.ConversionType.HtoK)),  # 敬称削除 + ひら -> カタ
    ]
    chk_pattern = sorted(set(chk_pattern), key=chk_pattern.index)  # 順序を維持したまま重複排除

    if g.params.individual or not_replace:
        for name in chk_pattern:
            if name in g.cfg.member.lists:  # メンバーリスト
                return name
            if name in g.cfg.member.all_lists:  # 別名を含むリスト
                if ret_name := g.cfg.member.resolve_name(name):
                    return ret_name
    else:
        for team in chk_pattern:
            if team in g.cfg.team.lists:  # チームリスト
                return team

    # リストに見つからない場合
    name = honor_remove(target)
    if g.params.unregistered_replace and not not_replace:
        name = g.cfg.member.guest_name
    if name != g.cfg.member.guest_name and add_mark:
        name = f"{name}({g.cfg.setting.guest_mark})"

    return name


def honor_remove(name: str) -> str:
    """
    敬称削除

    Args:
        name (str): 対象の名前

    Returns:
        str: 敬称を削除した名前

    """
    honor = r"(くん|さん|ちゃん|クン|サン|チャン|君)$"
    if re.match(rf".*{honor}", name):
        if not re.match(rf".*(っ|ッ|ー){honor}", name):
            name = re.sub(rf"{honor}", "", name)

    return name


def anonymous_mapping(name_list: list[str], initial: int = 0) -> dict[str, str]:
    """
    名前リストから変換用辞書を生成

    Args:
        name_list (list[str]): 名前リスト
        initial (int, optional): インデックス初期値. Defaults to 0.

    Returns:
        dict[str, str]: マッピング用辞書

    """
    ret: dict[str, str] = {}

    if g.params.individual:
        prefix = "Player"
        id_list = {x["name"]: x["id"] for x in g.cfg.member.info}
    else:
        prefix = "Team"
        id_list = {x["team"]: x["id"] for x in g.cfg.team.info}

    if len(name_list) == 1:
        name = name_list[0]
        if name in id_list:
            idx = id_list[name]
        else:
            idx = int(random.random() * 100 + 100)
        ret[name] = f"{prefix}_{idx + initial:03d}"
    else:
        random.shuffle(name_list)
        for idx, name in enumerate(name_list):
            ret[name] = f"{prefix}_{idx + initial:03d}"

    return ret


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
    if g.params.command:
        hide_items = hide_items.union(set(cast(SubCommands, getattr(g.cfg, g.params.command)).dropitems))

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

    rename_dict = dictutil.rename_dicts(
        item_list,
        StyleOptions(rename_type=StyleOptions.RenameType.NORMAL),
    )
    for k, v in rename_dict.items():
        if set([k, v]) & hide_items:
            hide_items = hide_items.union({k, v})

    rename_dict_short = dictutil.rename_dicts(
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


def group_strings(lines: list[str], limit: int = 3000) -> list[str]:
    """
    指定文字数まで改行で連結

    Args:
        lines (list[str]): 連結対象
        limit (int, optional): 制限値. Defaults to 3000.

    Returns:
        list[str]: 連結結果

    """
    result: list[str] = []
    buffer: list[str] = []

    for i, line in enumerate(lines):
        is_last = i == len(lines) - 1  # 最終ブロック判定
        max_char = limit * 1.5 if is_last else limit  # 1ブロックの最大値

        # 仮に追加したときの文字列長を計算
        temp = buffer + [line]
        total_len = len("".join(temp))

        if total_len <= max_char:
            buffer.append(line)
        else:
            if buffer:
                result.append("\n".join(buffer))
            buffer = [line]

    if buffer:
        result.append("\n".join(buffer))

    # 改行の集約
    result = [str(x).replace("\n```\n\n```\n", "\n```\n```\n") for x in result]
    result = [str(x).replace("\n\n\t", "\n\t") for x in result]

    return result
