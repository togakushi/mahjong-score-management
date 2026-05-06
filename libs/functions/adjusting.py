"""
libs/functions/adjusting.py
"""

import pandas as pd


def floatfmt(df: pd.DataFrame, index: bool = False) -> list[str]:
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


def add_units(df: pd.DataFrame, compact: bool = False) -> pd.DataFrame:
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
            case x if x.endswith(("ポイント", "(ポイント)")) or x == "区間平均":
                df[column_name] = df[column_name].map(
                    lambda v: str(v) if str(v).endswith("pt") else f"{float(v):+.1f}pt".replace("-", "▲"),
                )
                if compact:
                    new_name = "\n".join([x if x else "ポイント" for x in column_name.split("ポイント")])
                    df.rename(columns={column_name: new_name}, inplace=True)
            case x if x.endswith("数"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.0f}")
            case x if x.endswith("率"):
                df[column_name] = df[column_name].map(
                    lambda v: str(v) if str(v).endswith("%") else f"{float(v):.2f}%",
                )
            case "平均順位":
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.2f}")
                if compact:
                    df.rename(columns={column_name: "平均\n順位"}, inplace=True)
            case "playtime":
                df[column_name] = df[column_name].map(lambda v: str(v).replace("-", "/"))
            case x if x == "point" or x.endswith(("_point", "_total")):
                df[column_name] = df[column_name].map(
                    lambda v: str(v) if str(v).endswith("pt") else f"{float(v):+.1f}pt".replace("-", "▲"),
                )
            case x if x == "rpoint" or x.endswith("_rpoint"):
                df[column_name] = df[column_name].map(
                    lambda v: str(v) if str(v).endswith("点") else f"{float(v):+.0f}点".replace("-", "▲"),
                )
            case x if x == "rpoint_avg":
                df[column_name] = df[column_name].map(
                    lambda v: str(v) if str(v).endswith("点") else f"{float(v):.1f}点".replace("-", "▲"),
                )
            case x if x == "rank" or x.endswith("_rank"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.0f}位" if v.is_integer() else f"{v:.1f}位")
            case x if x.startswith("diff_from_"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.1f}pt" if pd.notna(v) else "------")
            case x if x == "rate" or x.endswith("_dev"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.1f}")

    return df
