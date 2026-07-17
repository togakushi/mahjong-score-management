"""
成績報告書
"""

import logging
import os
from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING, Any, Hashable, Literal

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, TableStyle

import libs.global_value as g
from libs.functions import adjusting, lookup, message
from libs.types import StyleOptions
from libs.utils import textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def get_game_results() -> list[list[str]]:
    """
    月/年単位のゲーム結果を集計する。

    Returns:
        list[list[str]]: 集計結果のリスト

    """
    df = adjusting.add_units(g.params.read_data("REPORT_PERSONAL_DATA"), True)
    if df.empty:
        return []

    # 0回の同着を削除
    for col in ("1.5位", "2.5位", "3.5位"):
        if not int(df[col].sum()):
            df.drop(columns=[f"{col}", f"{col}率"], inplace=True)

    results: list[list[str]] = [df.columns.to_list()]
    for x in df.T.to_dict(orient="list").values():
        results.append(x)

    logging.debug("return record: %s", len(results))
    return results


def get_count_results(game_count: int) -> list[list[str]]:
    """
    指定した間隔で区切ってゲーム結果を集計する。

    Args:
        game_count (int): 区切る対戦数

    Returns:
        list[list[str]]: 集計結果のリスト

    """
    g.params.interval = game_count
    df = adjusting.add_units(g.params.read_data("REPORT_COUNT_DATA"), True)
    if df.empty:
        return []

    # 0回の同着を削除
    for col in ("1.5位", "2.5位", "3.5位"):
        if not df[col].sum():
            df.drop(columns=[f"{col}", f"{col}率"], inplace=True)

    results: list[list[str]] = [df.columns.to_list()]
    for x in df.T.to_dict(orient="list").values():
        results.append(x)

    logging.debug("return record: %s", len(results))
    return results


def get_count_moving(game_count: int) -> list[dict[Hashable, Any]]:
    """
    移動平均を取得する。

    Args:
        game_count (int): 平滑化する対戦数

    Returns:
        list[dict[Hashable, Any]]: 集計結果のリスト

    """
    g.params.interval = game_count
    df = g.params.read_data("REPORT_COUNT_MOVING")
    results = df.to_dict(orient="records")

    logging.debug("return record: %s", len(results))
    return results


def graphing_mean_rank(df: pd.DataFrame, title: str, whole: bool = False) -> BytesIO:
    """
    平均順位の折れ線グラフを生成する。

    Args:
        df (pd.DataFrame): 描写データ
        title (str): グラフタイトル
        whole (bool, optional): 集計種別. Defaults to False.

            - *True*: 全体集計
            - *False*: 指定範囲集計

    Returns:
        BytesIO: 画像データ

    """
    imgdata = BytesIO()

    if whole:
        df.plot(
            kind="line",
            figsize=(12, 5),
            fontsize=14,
        )
        plt.legend(
            title="開始 - 終了",
            ncol=int(len(df.columns) / 5) + 1,
        )
    else:
        df.plot(
            kind="line",
            y="rank_avg",
            x="game_no",
            legend=False,
            figsize=(12, 5),
            fontsize=14,
        )

    plt.title(title, fontsize=18)
    plt.grid(axis="y")

    # Y軸設定
    plt.ylabel("平均順位", fontsize=14)
    plt.yticks([4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0])
    for ax in plt.gcf().get_axes():  # 逆向きにする
        ax.invert_yaxis()

    # X軸設定
    plt.xlabel("対戦数", fontsize=14)

    plt.savefig(imgdata, format="jpg", bbox_inches="tight")
    return imgdata


def graphing_total_points(df: pd.DataFrame, title: str, whole: bool = False) -> BytesIO:
    """
    通算ポイント推移の折れ線グラフを生成する。

    Args:
        df (pd.DataFrame): 描写データ
        title (str): グラフタイトル
        whole (bool, optional): 集計種別. Defaults to False.

            - *True*: 全体集計 / 移動平均付き
            - *False*: 指定範囲集計
    Returns:
        BytesIO: 画像データ

    """
    imgdata = BytesIO()

    if whole:
        df.plot(
            kind="line",
            figsize=(12, 8),
            fontsize=14,
        )
        plt.legend(
            title="通算 （ 開始 - 終了 ）",
            ncol=int(len(df.columns) / 5) + 1,
        )
    else:
        point_sum = df.plot(
            kind="line",
            y="point_sum",
            label="通算",
            figsize=(12, 8),
            fontsize=14,
        )
        if len(df) > 50:
            point_sum = (
                df["point_sum"]
                .rolling(40)
                .mean()
                .plot(
                    kind="line",
                    label="移動平均(40ゲーム)",
                    ax=point_sum,
                )
            )
        if len(df) > 100:
            point_sum = (
                df["point_sum"]
                .rolling(80)
                .mean()
                .plot(
                    kind="line",
                    label="移動平均(80ゲーム)",
                    ax=point_sum,
                )
            )
        plt.legend()

    plt.title(title, fontsize=18)
    plt.grid(axis="y")

    # Y軸設定
    plt.ylabel("ポイント", fontsize=14)
    ylocs, ylabs = plt.yticks()
    new_ylabs = [ylab.get_text().replace("−", "▲") for ylab in ylabs]
    plt.yticks(list(ylocs[1:-1]), new_ylabs[1:-1])

    # X軸設定
    plt.xlabel("対戦数", fontsize=14)

    plt.savefig(imgdata, format="jpg", bbox_inches="tight")
    return imgdata


def graphing_rank_distribution(df: pd.DataFrame, title: str) -> BytesIO:
    """
    順位分布の棒グラフを生成する。

    Args:
        df (pd.DataFrame): 描写データ
        title (str): グラフタイトル

    Returns:
        BytesIO: 画像データ

    """
    imgdata = BytesIO()

    df.plot(
        kind="bar",
        stacked=True,
        figsize=(12, 7),
        fontsize=14,
    )

    plt.title(title, fontsize=18)
    plt.legend(
        bbox_to_anchor=(0.5, 0),
        loc="lower center",
        ncol=4,
        fontsize=12,
    )

    # Y軸設定
    plt.yticks([0, 25, 50, 75, 100])
    plt.ylabel("（％）", fontsize=14)
    for ax in plt.gcf().get_axes():  # グリッド線を背後にまわす
        ax.set_axisbelow(True)
        plt.grid(axis="y")

    # X軸設定
    if len(df) > 10:
        plt.xticks(rotation=30, ha="right")
    else:
        plt.xticks(rotation=30)

    plt.savefig(imgdata, format="jpg", bbox_inches="tight")
    return imgdata


def gen_pdf(m: "MessageParserProtocol") -> None:
    """
    成績レポートを生成する

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.DETAILED_RESULTS

    if g.adapter.conf.plotting_backend == "plotly":
        m.post.reset()
        m.set_headline(message.random_reply(m, "not_implemented"), StyleOptions())
        return

    if not g.params.player_name:  # レポート対象の指定なし
        m.set_headline(message.random_reply(m, "no_target"), StyleOptions(title="成績レポート"))
        m.status.result = False
        return

    # 対象メンバーの記録状況
    target_info = lookup.member_info(g.params.placeholder())
    logging.debug(target_info)

    if not target_info["game_count"]:  # 記録なし
        m.set_headline(message.random_reply(m, "no_hits"), StyleOptions(title="成績レポート"))
        m.status.result = False
        return

    # 書式設定
    font_path = os.path.join(os.path.realpath(os.path.curdir), g.cfg.setting.font_file)
    pdf_path = g.cfg.setting.work_dir / (f"{g.params.filename}.pdf" if g.params.filename else "results.pdf")
    pdfmetrics.registerFont(TTFont("ReportFont", font_path))

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(A4),
        topMargin=10.0 * mm,
        bottomMargin=10.0 * mm,
        # leftMargin=1.5 * mm,
        # rightMargin=1.5 * mm,
    )

    style: dict[str, Any] = {}
    style["Title"] = ParagraphStyle(name="Title", fontName="ReportFont", fontSize=24)
    style["Normal"] = ParagraphStyle(name="Normal", fontName="ReportFont", fontSize=14)
    style["Left"] = ParagraphStyle(name="Left", fontName="ReportFont", fontSize=14, alignment=TA_LEFT)
    style["Right"] = ParagraphStyle(name="Right", fontName="ReportFont", fontSize=14, alignment=TA_RIGHT)

    plt.rcdefaults()
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = font_prop.get_name()
    fm.fontManager.addfont(font_path)

    # レポート作成
    elements: list[Any] = []
    elements.extend(cover_page(style, target_info))  # 表紙
    elements.extend(entire_aggregate(style))  # 全期間
    elements.extend(periodic_aggregation(style))  # 期間集計
    elements.extend(sectional_aggregate(style, target_info))  # 区間集計

    doc.build(elements)
    logging.debug("report generation: %s", g.params.player_name)

    m.set_message(pdf_path, StyleOptions(title=f"成績レポート({g.params.player_name})", use_comment=True, header_hidden=True))


def cover_page(style: dict[str, Any], target_info: dict[str, Any]) -> list[Any]:
    """
    表紙生成

    Args:
        style (dict[str, Any]): レイアウトスタイル
        target_info (dict[str, Any]): プレイヤー情報

    Returns:
        list[Any]: 生成内容

    """
    elements: list[Any] = []

    first_game = datetime.fromtimestamp(  # 最初のゲーム日時
        float(target_info["first_game"])
    )
    last_game = datetime.fromtimestamp(  # 最後のゲーム日時
        float(target_info["last_game"])
    )

    if g.params.anonymous:
        mapping_dict = textutil.anonymous_mapping([g.params.player_name])
        target_player = next(iter(mapping_dict.values()))
    else:
        target_player = g.params.player_name

    # 表紙
    elements.append(Spacer(1, 40 * mm))
    elements.append(Paragraph(f"成績レポート：{target_player}", style["Title"]))
    elements.append(Spacer(1, 10 * mm))
    elements.append(
        Paragraph(
            f"集計期間：{first_game.strftime('%Y-%m-%d %H:%M')} - {last_game.strftime('%Y-%m-%d %H:%M')}",
            style["Normal"],
        )
    )
    elements.append(Spacer(1, 100 * mm))
    elements.append(Paragraph(f"作成日：{datetime.now().strftime('%Y-%m-%d')}", style["Right"]))
    elements.append(PageBreak())

    return elements


def entire_aggregate(style: dict[str, Any]) -> list[Any]:
    """
    全期間

    Args:
        style (dict[str, Any]): レイアウトスタイル

    Returns:
        list[Any]: 生成内容

    """
    elements: list[Any] = []

    elements.append(Paragraph("全期間", style["Left"]))
    elements.append(Spacer(1, 5 * mm))
    g.params.aggregate_unit = "A"
    tmp_data = get_game_results()

    if not tmp_data:
        return []

    # --- テーブルデータ生成
    data: list[list[str]] = []
    for val in tmp_data:  # 対戦数を除外
        data.append(val[1:])

    cell_style = [
        ("FONT", (0, 0), (-1, -1), "ReportFont", 10),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        # ヘッダ行
        ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ]
    for idx, col in enumerate(data[0]):  # 獲得数と獲得率を結合
        if col.endswith("率"):
            cell_style.append(
                ("SPAN", (idx - 1, 0), (idx, 0)),
            )

    tt = LongTable(data, repeatRows=1)
    tt.setStyle(TableStyle(cell_style))  # type: ignore[arg-type]
    elements.append(tt)

    # 順位分布
    imgdata = BytesIO()
    rank_dist_label: list[str] = []
    rank_dist_data: list[float] = []
    for idx, col in enumerate(data[0]):
        if col.startswith(("1", "2", "3", "4")) and col.endswith("率"):
            rank_dist_label.append(col)
            rank_dist_data.append(float(data[1][idx].replace("%", "")))
    gdata = pd.DataFrame(
        {"順位分布": rank_dist_data},
        index=rank_dist_label,
    )
    gdata.plot(
        kind="pie",
        y="順位分布",
        labels=None,
        figsize=(6, 6),
        fontsize=14,
        autopct="%.2f%%",
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    plt.title("順位分布 （ 全期間 ）", fontsize=18)
    plt.ylabel("")
    plt.legend(
        labels=list(gdata.index),
        bbox_to_anchor=(0.5, -0.1),
        loc="lower center",
        ncol=4,
        fontsize=12,
    )
    plt.savefig(imgdata, format="jpg", bbox_inches="tight")

    elements.append(Spacer(1, 5 * mm))
    elements.append(Image(imgdata, width=600 * 0.5, height=600 * 0.5))

    df = pd.DataFrame(get_count_moving(0))
    df["playtime"] = pd.to_datetime(df["playtime"])

    # 通算ポイント推移
    imgdata = graphing_total_points(df, "通算ポイント推移 （ 全期間 ）", False)
    elements.append(Image(imgdata, width=1200 * 0.5, height=800 * 0.5))

    # 平均順位
    imgdata = graphing_mean_rank(df, "平均順位推移 （ 全期間 ）", False)
    elements.append(Image(imgdata, width=1200 * 0.5, height=500 * 0.5))

    elements.append(PageBreak())

    return elements


def periodic_aggregation(style: dict[str, Any]) -> list[Any]:
    """
    期間集計

    Args:
        style (dict[str, Any]): レイアウトスタイル

    Returns:
        list[Any]: 生成内容

    """
    elements: list[Any] = []
    rank_dist_label: list[str] = []
    rank_dist_data: dict[str, list[float]] = {}

    pattern: list[tuple[str, str, Literal["A", "M", "Y"]]] = [
        # 表タイトル, グラフタイトル, フラグ
        ("月別集計", "順位分布（月別）", "M"),
        ("年別集計", "順位分布（年別）", "Y"),
    ]

    for table_title, graph_title, flag in pattern:
        elements.append(Paragraph(table_title, style["Left"]))
        elements.append(Spacer(1, 5 * mm))

        g.params.aggregate_unit = flag
        data = get_game_results()

        if not data:
            return []

        # --- テーブルデータ生成
        cell_style = [
            ("FONT", (0, 0), (-1, -1), "ReportFont", 10),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            # ヘッダ行
            ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]
        for idx, val in enumerate(data[0]):  # 獲得数と獲得率を結合
            if val.endswith("率"):
                cell_style.append(
                    ("SPAN", (idx - 1, 0), (idx, 0)),
                )

        tt = LongTable(data, repeatRows=1)
        ts = TableStyle(cell_style)  # type: ignore[arg-type]

        if len(data) > 4:
            for i in range(len(data) - 2):
                if i % 2 == 0:
                    ts.add("BACKGROUND", (0, i + 2), (-1, i + 2), colors.lightgrey)
        tt.setStyle(ts)
        elements.append(tt)
        elements.append(Spacer(1, 10 * mm))

        # 順位分布
        rank_dist_label = [data[x + 1][0] for x in range(len(data) - 1)]
        rank_dist_data.clear()
        for idx, col in enumerate(data[0]):
            if col.startswith(("1", "2", "3", "4")) and col.endswith("率"):
                rank_dist_data.update({col: [float(data[x + 1][idx].replace("%", "")) for x in range(len(data) - 1)]})

        df = pd.DataFrame(rank_dist_data, index=rank_dist_label)
        imgdata = graphing_rank_distribution(df, graph_title)
        elements.append(Spacer(1, 5 * mm))
        elements.append(Image(imgdata, width=1200 * 0.5, height=700 * 0.5))

        elements.append(PageBreak())

    return elements


def sectional_aggregate(style: dict[str, Any], target_info: dict[str, Any]) -> list[Any]:
    """
    区間集計

    Args:
        style (dict[str, Any]): レイアウトスタイル
        target_info (dict[str, Any]): プレイヤー情報

    Returns:
        list[Any]: 生成内容

    """
    elements: list[Any] = []

    pattern: list[tuple[int, int, str]] = [
        # 区切り回数, 閾値, タイトル
        (80, 100, "短期"),
        (200, 240, "中期"),
        (400, 500, "長期"),
    ]

    for count, threshold, title in pattern:
        if target_info["game_count"] > threshold:
            # テーブル
            elements.append(Paragraph(f"区間集計 （ {title} ）", style["Left"]))
            elements.append(Spacer(1, 5 * mm))
            data = get_count_results(count)

            if not data:
                return []

            # --- テーブルデータ生成
            cell_style = [
                ("FONT", (0, 0), (-1, -1), "ReportFont", 10),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                # ヘッダ行
                ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ]
            for idx, val in enumerate(data[0]):  # 獲得数と獲得率を結合
                if val.endswith("率"):
                    cell_style.append(
                        ("SPAN", (idx - 1, 0), (idx, 0)),
                    )

            tt = LongTable(data, repeatRows=1)
            ts = TableStyle(cell_style)  # type: ignore[arg-type]
            if len(data) > 4:
                for i in range(len(data) - 2):
                    if i % 2 == 0:
                        ts.add("BACKGROUND", (0, i + 2), (-1, i + 2), colors.lightgrey)
            tt.setStyle(ts)
            elements.append(tt)

            # 順位分布
            df = pd.DataFrame(
                {
                    "1位率": [float(str(data[x + 1][6]).replace("%", "")) for x in range(len(data) - 1)],
                    "2位率": [float(str(data[x + 1][8]).replace("%", "")) for x in range(len(data) - 1)],
                    "3位率": [float(str(data[x + 1][10]).replace("%", "")) for x in range(len(data) - 1)],
                    "4位率": [float(str(data[x + 1][12]).replace("%", "")) for x in range(len(data) - 1)],
                },
                index=[f"{str(data[x + 1][0])} - {str(data[x + 1][1])}" for x in range(len(data) - 1)],
            )

            imgdata = graphing_rank_distribution(df, f"順位分布 （ 区間 {title} ）")
            elements.append(Spacer(1, 5 * mm))
            elements.append(Image(imgdata, width=1200 * 0.5, height=800 * 0.5))

            # 通算ポイント推移
            tmp_df = pd.DataFrame(get_count_moving(count))
            df = pd.DataFrame()
            for i in sorted(tmp_df["interval"].unique().tolist()):
                list_data = tmp_df[tmp_df.interval == i]["point_sum"].to_list()
                game_count = tmp_df[tmp_df.interval == i]["total_count"].to_list()
                df[f"{min(game_count)} - {max(game_count)}"] = [None] * (count - len(list_data)) + list_data

            imgdata = graphing_total_points(df, f"通算ポイント推移（区間 {title}）", True)
            elements.append(Image(imgdata, width=1200 * 0.5, height=800 * 0.5))

            # 平均順位
            df = pd.DataFrame()
            for i in sorted(tmp_df["interval"].unique().tolist()):
                list_data = tmp_df[tmp_df.interval == i]["rank_avg"].to_list()
                game_count = tmp_df[tmp_df.interval == i]["total_count"].to_list()
                df[f"{min(game_count)} - {max(game_count)}"] = [None] * (count - len(list_data)) + list_data

            imgdata = graphing_mean_rank(df, f"平均順位推移（区間 {title}）", True)
            elements.append(Image(imgdata, width=1200 * 0.5, height=500 * 0.5))

            elements.append(PageBreak())

    return elements
