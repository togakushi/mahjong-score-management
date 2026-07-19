"""
libs/functions/compose/text_item.py
"""

from typing import TYPE_CHECKING, Optional

import libs.global_value as g
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from libs.utils.timekit import Format


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


def date_range(
    kind: "Format",
    prefix_a: Optional[str] = None,
    prefix_b: Optional[str] = None,
) -> str:
    """
    日付範囲文字列

    Args:
        kind (Format): ExtendedDatetimeのformatメソッドに渡す引数
        prefix_a (str, optional): 単独で返った時の接頭辞. Defaults to None.
        prefix_b (str, optional): 範囲で返った時の接頭辞. Defaults to None.

    Returns:
        str: 生成文字列

    """
    ret: str
    str_st: str
    str_et: str
    st = ExtDt(g.params.starttime)
    et = ExtDt(g.params.endtime)
    ot = ExtDt(g.params.onday)

    if kind.name.endswith("_O"):
        str_st = st.format(kind)
        str_et = ot.format(kind)
    else:
        str_st = st.format(kind)
        str_et = et.format(kind)

    if st.format(kind, ExtDt.DEM.NUMBER) == ot.format(kind, ExtDt.DEM.NUMBER):
        if prefix_a and prefix_b:
            ret = f"{prefix_a} ({str_st})"
        else:
            ret = f"{str_st}"
    else:
        if prefix_a and prefix_b:
            ret = f"{prefix_b} ({str_st} - {str_et})"
        else:
            ret = f"{str_st} - {str_et}"

    return ret
