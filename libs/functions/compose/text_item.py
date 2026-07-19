"""
libs/functions/compose/text_item.py
"""

import libs.global_value as g


def search_word(headword: bool = False) -> str:
    """
    キーワード検索条件を返す

    Args:
        headword (bool, optional): 見出しを付ける. Defaults to False.

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
