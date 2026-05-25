"""
libs/utils/formatter.py
"""

from typing import Optional, cast

import libs.global_value as g
from libs.domain.section import SubCommands
from libs.types import StyleOptions
from libs.utils import dictutil


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
