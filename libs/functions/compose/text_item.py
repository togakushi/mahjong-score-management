"""
libs/functions/compose/text_item.py
"""

from typing import TYPE_CHECKING, Optional

from table2ascii import Alignment, PresetStyle, table2ascii

import libs.global_value as g
from libs.types import CommandType
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from libs.utils.timekit import Format


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


def get_members_list() -> str:
    """
    登録済みのメンバー一覧を取得する

    Returns:
        str: メンバーリスト

    """
    name_list: list[list[str]] = []
    for pname in g.cfg.member.lists:
        name_list.append([pname, ", ".join(g.cfg.member.alias(pname))])

    if name_list:
        output = table2ascii(
            header=["表示名", "登録されている名前"],
            body=name_list,
            alignments=[Alignment.LEFT, Alignment.LEFT],
            style=PresetStyle.ascii_borderless,
        )
    else:
        output = "メンバーは登録されていません。"

    return output


def get_team_list() -> str:
    """
    チームの登録状況を取得する

    Returns:
        str: チームリスト

    """
    team_list: list[list[str]] = []
    for team_name in g.cfg.team.lists:
        if member := ", ".join(g.cfg.team.member(team_name)):
            team_list.append([team_name, member])
        else:
            team_list.append([team_name, "未エントリー"])

    if team_list:
        output = table2ascii(
            header=["チーム名", "所属メンバー"],
            body=team_list,
            alignments=[Alignment.LEFT, Alignment.LEFT],
            style=PresetStyle.ascii_borderless,
        )
    else:
        output = "チームは登録されていません。"

    return output
