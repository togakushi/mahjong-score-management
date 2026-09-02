"""
libs/functions/badge.py
"""

import math

import libs.global_value as g


def degree(game_count: int = 0) -> str:
    """
    対戦数に対して表示される称号を返す

    Args:
        game_count (int, optional): 対戦数。 Defaults to 0.

    Returns:
        str: 表示する称号

    """
    badge: str = ""

    if g.adapter.conf.badge_degree:
        if degree_list := g.cfg.main_parser.get("degree", "badge", fallback=""):
            degree_badge = degree_list.split(",")
        else:
            return ""
        if counter_list := g.cfg.main_parser.get("degree", "counter", fallback=""):
            degree_counter = list(map(int, counter_list.split(",")))
            for idx, val in enumerate(degree_counter):
                if game_count >= val:
                    badge = degree_badge[idx]

    return badge


def status(game_count: int = 0, win: int = 0) -> str:
    """
    勝率に対して付く調子バッジを返す

    Args:
        game_count (int, optional): 対戦数。 Defaults to 0.
        win (int, optional): 勝ち数。 Defaults to 0.

    Returns:
        str: 表示する称号

    """
    badge: str = ""

    if g.adapter.conf.badge_status:
        if status_list := g.cfg.main_parser.get("status", "badge", fallback=""):
            status_badge = status_list.split(",")
        else:
            return badge

        if status_step := g.cfg.main_parser.getfloat("status", "step", fallback=""):
            if not isinstance(status_step, float):
                return badge
            if game_count == 0:
                index = 0
            else:
                winper = win / game_count * 100
                index = 3
                for i in (1, 2, 3):
                    if winper <= 50 - status_step * i:
                        index = 4 - i
                    if winper >= 50 + status_step * i:
                        index = 2 + i

            badge = status_badge[index]

    return badge


def grade(name: str, detail: bool = True) -> str:
    """
    段位表示

    Args:
        name (str): 対象プレイヤー名
        detail (bool, optional): 昇段ポイントの表示。 Defaults to True.

    Returns:
        str: 称号

    """

    def _promotion_check(grade_level: int, point: int, rank: int) -> tuple[int, int]:
        """
        昇段チェック

        Args:
            grade_level (int): 現在のレベル(段位)
            point (int): 現在の昇段ポイント
            rank (int): 獲得順位

        Returns:
            tuple[int, int]: チェック後の昇段ポイント, チェック後のレベル(段位)

        """
        tbl_data = g.cfg.badge.grade.table["table"]
        new_point = point + int(tbl_data[grade_level]["acquisition"][rank - 1])

        if new_point >= int(tbl_data[grade_level]["point"][1]):  # level up
            grade_level = min(grade_level + 1, len(tbl_data) - 1)
            new_point = int(tbl_data[grade_level]["point"][0])  # 初期値
        elif new_point < 0:  # level down
            new_point = int(0)
            if tbl_data[grade_level]["demote"]:
                grade_level = max(grade_level - 1, 0)
                new_point = int(tbl_data[grade_level]["point"][0])  # 初期値

        return (new_point, grade_level)

    if not g.cfg.badge.grade.table_name or not g.cfg.badge.grade.table:  # テーブル未定義
        return ""

    if name not in g.cfg.member.lists:  # ゲスト
        if guest_title := g.cfg.badge.get("guest_title"):
            return str(guest_title)
        else:
            return ""

    if not g.adapter.conf.badge_grade:  # 非表示
        return ""

    # 初期値
    point: int = 0  # 昇段ポイント
    grade_level: int = 0  # レベル(段位)
    g.params.player_name = name

    result_df = g.params.read_data("SELECT_ALL_RESULTS")
    addition_expression = g.cfg.badge.grade.table.get("addition_expression", "0")
    for _, data in result_df.iterrows():
        rank = data["rank"]
        rpoint = data["rpoint"]
        addition_point = math.ceil(eval(addition_expression.format(rpoint=rpoint, origin_point=g.params.origin_point)))
        point, grade_level = _promotion_check(grade_level, point + addition_point, rank)

    next_point = g.cfg.badge.grade.table["table"][grade_level]["point"][1]
    grade_name = g.cfg.badge.grade.table["table"][grade_level]["grade"]
    point_detail = f" ({point}/{next_point})" if detail else ""

    return f"{grade_name}{point_detail}"
