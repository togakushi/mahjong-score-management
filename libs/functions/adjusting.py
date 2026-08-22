"""
libs/functions/adjusting.py
"""

from typing import Optional

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
            case "対戦数" | "win" | "lose" | "draw" | "top2" | "top3":
                fmt.append(".0f")
            case "通算" | "通算ポイント" | "point_sum":
                fmt.append("+.1f")
            case "平均" | "平均ポイント" | "point_avg" | "平均収支" | "区間ポイント" | "区間平均":
                fmt.append("+.1f")
            case "1位(ポイント)" | "2位(ポイント)" | "3位(ポイント)" | "4位(ポイント)" | "5位(ポイント)":
                fmt.append("+.1f")
            case "1位" | "2位" | "3位" | "4位" | "rank1" | "rank2" | "rank3" | "rank4":
                fmt.append(".0f")
            case "トビ" | "flying":
                fmt.append(".0f")
            case "平均順位" | "平順" | "rank_avg":
                fmt.append(".2f")
            case "順位差" | "トップ差" | "平均素点":
                fmt.append(".1f")
            case v if v.endswith("_avg_diff"):
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
                case "プレイヤー名" | "チーム名" | "name" | "team" | "player":
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

    def format_cell(
        v: object,
        unit: Optional[str] = None,
        signed: bool = False,
        digits: int = 0,
        nan_text: Optional[str] = None,
        negative_symbol: bool = True,
    ) -> str:
        ret: str = ""
        if isinstance(v, float) and pd.isna(v):
            return nan_text if nan_text else "該当なし"
        elif isinstance(v, str):
            if not v.strip():
                return nan_text if nan_text else "該当なし"
            if unit is not None and v.endswith(unit):
                return v
        else:
            try:
                v = float(v)  # type: ignore
            except ValueError:
                return str(v)
            except TypeError:
                return str(v)

        match unit:
            case x if x is None:
                try:
                    ret = f"{v:.{digits}f}"
                except ValueError:
                    ret = str(v)
            case "位":
                ret = f"{v:.0f}位" if isinstance(v, float) and v.is_integer() else f"{v:.{digits}f}位"
            case _:
                if isinstance(v, str):
                    ret = v
                elif signed:
                    ret = f"{v:+.{digits}f}{unit}".replace("-", "▲")
                elif negative_symbol:
                    ret = f"{v:.{digits}f}{unit}".replace("-", "▲")
                else:
                    ret = f"{v:.{digits}f}{unit}"

        return ret

    for column_name in df.columns:
        match column_name:
            # ポイント
            case x if x in {"point", "point_max", "区間平均"} or x.endswith(("ポイント", "(ポイント)", "_point", "_total")):
                df[column_name] = [format_cell(v, "pt", True, 1) for v in df[column_name]]
                if compact and x.endswith("ポイント"):
                    new_name = "\n".join([x if x else "ポイント" for x in column_name.split("ポイント")])
                    df.rename(columns={column_name: new_name}, inplace=True)
                    df[new_name] = df[new_name].astype(str)
            case x if x.startswith("point") and x.endswith(tuple(map(str, range(1, 6)))):
                df[column_name] = [format_cell(v, "pt", True, 1) for v in df[column_name]]
            case x if x.startswith("diff_from_"):
                df[column_name] = [format_cell(v, "pt", False, 1, "-------") for v in df[column_name]]
            case x if x == "deposit":
                df[column_name] = [format_cell(v, "pt", False, 1, negative_symbol=True) for v in df[column_name]]
            case "consecutive_record":
                for idx, record in df["consecutive_record"].items():
                    point = [format_cell(float(pt), "pt", True, 1) for pt in str(record).split()]
                    df.at[idx, column_name] = " ".join(point)
            # 素点
            case x if x in ["rpoint_avg", "avg_balance"] or x.endswith("_avg_diff"):
                df[column_name] = [format_cell(v, "点", True, 1) for v in df[column_name]]
            case x if x == "rpoint" or x.endswith(("_rpoint", "_diff")):
                df[column_name] = [format_cell(v, "点", True, 0) for v in df[column_name]]
            case x if x in ["rpoint_max", "rpoint_min"]:
                df[column_name] = [format_cell(v, "点", False, negative_symbol=True) for v in df[column_name]]
            # 個数/率
            case x if x.endswith("数"):
                df[column_name] = [format_cell(v) for v in df[column_name]]
            case x if x.endswith(("率", "_rate")):
                df[column_name] = [format_cell(v, "%", False, 2) for v in df[column_name]]
            case x if x.endswith("(%)"):
                df[column_name] = df[column_name].map(lambda v: f"{float(v):.2%}")
            # 順位
            case x if x in {"平均順位", "rank_avg"}:
                df[column_name] = [format_cell(v, digits=2) for v in df[column_name]]
                if compact and x == "平均順位":
                    df.rename(columns={column_name: "平均\n順位"}, inplace=True)
            case x if (x == "rank" or x.endswith("_rank")) and x != "acquisition_rank":
                df[column_name] = [format_cell(v, "位", False, 1) for v in df[column_name]]
            # レコード
            case x if x.endswith("_max"):
                df[column_name] = [format_cell(v, "連続", False, 0) for v in df[column_name]]
            # その他
            case "playtime":
                df[column_name] = df[column_name].map(lambda v: str(v).replace("-", "/"))
            case "elapsed_day":
                df[column_name] = [format_cell(v, "日", False, 0, "---") for v in df[column_name]]
            case "game_count":
                df[column_name] = [format_cell(v, "", False, 0, "---") for v in df[column_name]]
            case x if x == "rate" or x.endswith("_dev"):
                df[column_name] = [format_cell(v, digits=1) for v in df[column_name]]

        if column_name in df.columns:
            df[column_name] = df[column_name].astype(str)

    return df
