"""
libs/utils/graphutil.py
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import use

import libs.global_value as g
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from libs.utils.timekit import Format


def setup() -> None:
    """グラフ設定初期化"""
    pd.options.plotting.backend = g.adapter.conf.plotting_backend
    match g.adapter.conf.plotting_backend:
        case "plotly":
            return
        case _:
            pass  # 以下に処理をベタ書き

    plt.close()
    plt.rcdefaults()

    use(backend="agg")
    mlogger = logging.getLogger("matplotlib")
    mlogger.setLevel(logging.WARNING)

    # スタイルの適応
    if (style := g.cfg.setting.graph_style) not in plt.style.available:
        style = "ggplot"
    plt.style.use(style)

    # フォント再設定
    plt.rcParams["font.family"] = []
    plt.rcParams["font.serif"] = []
    plt.rcParams["font.sans-serif"] = []
    plt.rcParams["font.cursive"] = []
    plt.rcParams["font.fantasy"] = []
    plt.rcParams["font.monospace"] = []

    fm.fontManager.addfont(g.cfg.setting.font_file)
    font_prop = fm.FontProperties(fname=g.cfg.setting.font_file)
    plt.rcParams["font.family"] = font_prop.get_name()

    # グリッド線
    if not plt.rcParams["axes.grid"]:
        plt.rcParams["axes.grid"] = True
        plt.rcParams["grid.alpha"] = 0.3
        plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["axes.axisbelow"] = True


def gen_xlabel(game_count: int) -> str:
    """
    X軸ラベル生成

    Args:
        game_count (int): 対戦数

    Returns:
        str: X軸ラベル

    """
    if g.params.target_count:
        xlabel = f"直近 {game_count} ゲーム"
    else:
        xlabel = f"集計日（{game_count} ゲーム）"
        match g.params.collection:
            case "daily":
                xlabel = f"集計日（{game_count} ゲーム）"
            case "monthly":
                xlabel = f"集計月（{game_count} ゲーム）"
            case "yearly":
                xlabel = f"集計年（{game_count} ゲーム）"
            case "all":
                xlabel = f"対戦数：{game_count} ゲーム"
            case _:
                if g.params.search_word:
                    xlabel = f"対戦数：{game_count} ゲーム"
                else:
                    xlabel = f"ゲーム終了日時（{game_count} ゲーム）"

    return xlabel


def xticks_parameter(days_list: list[Any]) -> dict[str, Any]:
    """
    X軸(xticks)に渡すパラメータを生成

    Args:
        days_list (list[Any]): 日付リスト

    Returns:
        dict[str, Any]: パラメータ

    """
    days_list = [str(x).replace("-", "/") for x in days_list]

    thresholds = [
        # データ数, 傾き, 位置
        (3, 0, "center"),
        (20, -30, "left"),
        (40, -45, "left"),
        (80, -60, "left"),
        (float("inf"), -90, "center"),
    ]

    for limit, rotation, position in thresholds:
        if len(days_list) <= limit:
            break

    return {
        "ticks": list(range(len(days_list)))[:: int(len(days_list) / 25) + 1],
        "labels": days_list[:: int(len(days_list) / 25) + 1],
        "rotation": rotation,
        "ha": position,
    }


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
