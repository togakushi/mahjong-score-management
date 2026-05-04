"""
libs/utils/formatter.py
"""

import random
import re
from typing import Optional, cast

import pandas as pd

import libs.global_value as g
from libs.bootstrap.section import SubCommands
from libs.types import StyleOptions
from libs.utils import textutil


def floatfmt_adjust(df: pd.DataFrame, index: bool = False) -> list[str]:
    """
    カラム名に応じたfloatfmtのリストを返す

    Args:
        df (pd.DataFrame): チェックするデータ
        index (bool, optional): リストにIndexを含める. Defaults to False.

    Returns:
        list[str]: floatfmtに指定するリスト

    """
    fmt: list[str] = []
    if df.empty:
        return fmt

    field: list[str] = df.columns.tolist()
    if index:
        field.insert(0, str(df.index.name))

    for x in field:
        match x:
            case v if v.endswith("_rate") or v.endswith("率") or v.endswith("(%)"):
                fmt.append(".2%")
            case v if v.endswith("_count"):
                fmt.append(".0f")
            case "ゲーム数" | "win" | "lose" | "draw" | "top2" | "top3":
                fmt.append(".0f")
            case "通算" | "通算ポイント" | "point_sum":
                fmt.append("+.1f")
            case "平均" | "平均ポイント" | "point_avg" | "平均収支" | "区間ポイント" | "区間平均":
                fmt.append("+.1f")
            case "1位(ポイント)" | "2位(ポイント)" | "3位(ポイント)" | "4位(ポイント)" | "5位(ポイント)":
                fmt.append("+.1f")
            case "1st" | "2nd" | "3rd" | "4th" | "1位" | "2位" | "3位" | "4位" | "rank1" | "rank2" | "rank3" | "rank4":
                fmt.append(".0f")
            case "トビ" | "flying":
                fmt.append(".0f")
            case "平均順位" | "平順" | "rank_avg":
                fmt.append(".2f")
            case "順位差" | "トップ差" | "平均素点":
                fmt.append(".1f")
            case "rpoint_max" | "rpoint_min" | "rpoint_mean":
                fmt.append(".0f")
            case _:
                fmt.append("")

    return fmt


def column_alignment(df: pd.DataFrame, header: bool = False, index: bool = False) -> list[str]:
    """
    カラム位置

    Args:
        df (pd.DataFrame): チェックするデータ
        header (bool, optional): ヘッダを対象にする
        index (bool, optional): リストにIndexを含める. Defaults to False.

    Returns:
        list[str]: colalignに指定するリスト

    """
    fmt: list[str] = []  # global, right, center, left, decimal, None
    if df.empty:
        return fmt

    field: list[str] = df.columns.tolist()
    if index:
        field.insert(0, str(df.index.name))

    if header:  # ヘッダ(すべて左寄せ)
        fmt = ["left"] * len(field)
    else:
        for x in field:
            match x:
                case "日時" | "playtime":
                    fmt.append("left")
                case "プレイヤー名" | "name" | "team" | "player":
                    fmt.append("left")
                case "内容" | "和了役" | "matter":
                    fmt.append("left")
                case "段位" | "grade":
                    fmt.append("left")
                case "順位分布" | "rank_distr" | "rank_distr4":
                    fmt.append("left")
                case "平均順位" | "rank_avg":
                    fmt.append("center")
                case _:
                    fmt.append("right")

    return fmt


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
        "flying": {"トビ", "トビ率", "飛", "flying", "flying_mix", "flying_count", "flying_rate", "flying_rate-count"},
        "yakuman": {"役満", "役満和了", "役満和了率", "yakuman_mix", "yakuman_count", "yakuman_rate", "yakuman_rate-count"},
        "regulation": {"卓外", "卓外清算", "卓外ポイント"},
        "other": {"その他", "メモ"},
    }
    for words_set in related_words_set.values():
        if hide_items & words_set:
            hide_items = hide_items.union(words_set)

    rename_dict = gen_rename_dict(
        item_list,
        StyleOptions(rename_type=StyleOptions.RenameType.NORMAL),
    )
    for k, v in rename_dict.items():
        if set([k, v]) & hide_items:
            hide_items = hide_items.union({k, v})

    rename_dict_short = gen_rename_dict(
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


def gen_rename_dict(columns: list[str], options: StyleOptions) -> dict[str, str]:
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
        "total_count": "集計ゲーム数",
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
        #
        "rank1_rate-count": "1位率(回)",
        "rank1_rate": "1位率",
        "rank2_rate-count": "2位率(回)",
        "rank2_rate": "2位率",
        "rank3_rate-count": "3位率(回)",
        "rank3_rate": "3位率",
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
        # 収支
        "avg_balance": "平均収支",
        "top2_balance": "連対収支",
        "lose2_balance": "逆連対収支",
        "rank1_balance": "1位収支",
        "rank2_balance": "2位収支",
        "rank3_balance": "3位収支",
        "rank4_balance": "4位収支",
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
                rename_dict[x] = "ゲーム数"
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
            case "1st" | "rank1" | "1st_count" | "1st_mix":
                rename_dict[x] = "1位数"
            case "2nd" | "rank2" | "2nd_count" | "2nd_mix":
                rename_dict[x] = "2位数"
            case "3rd" | "rank3" | "3rd_count" | "3rd_mix":
                rename_dict[x] = "3位数"
            case "4th" | "rank4" | "4th_count" | "4th_mix":
                rename_dict[x] = "4位数"
            case "flying" | "flying_mix":
                rename_dict[x] = "飛" if short else "トビ"
            case "pt_diff":
                rename_dict[x] = "差分"
            case "diff_from_above":
                rename_dict[x] = "順位差"
            case "diff_from_top":
                rename_dict[x] = "トップ差"
            case "yakuman_mix":
                rename_dict[x] = "役満和了"
            case "yakuman_count" | "yakuman":
                rename_dict[x] = "役満和了数"
            case "yakuman_rate":
                rename_dict[x] = "役満和了率"
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

    if not g.params.individual:
        rename_dict.update(name="チーム" if short else "チーム名")

    return rename_dict


def df_rename(df: pd.DataFrame, options: StyleOptions) -> pd.DataFrame:
    """
    カラム名をリネームする

    Args:
        df (pd.DataFrame): 対象データフレーム
        options (StyleOptions): 変換モード

    Returns:
        pd.DataFrame: リネーム後のデータフレーム

    """
    rename_dict = gen_rename_dict(df.columns.to_list(), options)

    return df.rename(columns=rename_dict)


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


def split_strings(msg: str, limit: int = 3000) -> list[str]:
    """
    指定文字数で分割

    Args:
        msg (str): 分割対象
        limit (int, optional): 分割文字数. Defaults to 3000.

    Returns:
        list[str]: 分割結果

    """
    result: list[str] = []
    buffer: list[str] = []
    codeblock: bool = False

    for line in msg.splitlines(keepends=True):
        # 仮に追加したときの文字列長を計算
        temp = buffer + [line]
        total_len = len("".join(temp))

        if total_len < limit:
            buffer.append(line)
            if line != line.replace("```", ""):  # 1行でopen/closeされる想定ではない
                codeblock = not (codeblock)
        else:
            if buffer:
                if codeblock:  # codeblock open状態
                    buffer.append("```\n")
                    result.append("".join(buffer))
                    buffer = [f"```\n{line}"]
                else:
                    result.append("".join(buffer))
                    buffer = [line]

    if result:
        return result
    return [msg]


def adjusting_values(df: pd.DataFrame, compact: bool = False) -> pd.DataFrame:
    """
    単位の追加、桁数の調整

    Args:
        df (pd.DataFrame): 対象データ
        compact (bool): カラム名を折り返す

    Returns:
        pd.DataFrame: 調整後のデータ

    """
    for column_name in df.columns:
        match column_name:
            case x if x.endswith("ポイント"):
                df[column_name] = df[column_name].map(lambda v: str(v) if str(v).endswith("pt") else f"{float(v):+.1f}pt".replace("-", "▲"))
                if compact:
                    new_name = "\n".join([x if x else "ポイント" for x in column_name.split("ポイント")])
                    df.rename(columns={column_name: new_name}, inplace=True)
            case x if x.endswith("率"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.2f}%")
            case "平均順位":
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.2f}")
                if compact:
                    df.rename(columns={column_name: "平均\n順位"}, inplace=True)
            case "playtime":
                df[column_name] = df[column_name].map(lambda v: str(v).replace("-", "/"))
            case x if x == "point" or x.endswith(("_point", "_total")):
                df[column_name] = df[column_name].map(lambda v: str(v) if str(v).endswith("pt") else f"{float(v):+.1f}pt".replace("-", "▲"))
            case x if x == "rpoint" or x.endswith("_rpoint"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.0f}点".replace("-", "▲"))
            case x if x == "rank" or x.endswith("_rank"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.0f}位" if v.is_integer() else f"{v:.1f}位")
            case x if x.startswith("diff_from_"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.1f}pt" if pd.notna(v) else "------")

    return df
