"""
平均順位/平均素点の分散図
"""

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm  # type: ignore[import-untyped]
from matplotlib.lines import Line2D

import libs.global_value as g
from libs.domain.datamodels import GameInfo
from libs.functions import message
from libs.types import CommandType, StyleOptions
from libs.utils import graphutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def plot(m: "MessageParserProtocol") -> None:
    """
    平均順位と平均素点の分散図を生成する

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    # パラメータ更新
    m.status.command_type = CommandType.ANALYSIS_SCORES

    # ヘッダ情報
    game_info = GameInfo()
    title_text = "順位素点相関図"

    # データ収集
    df = g.params.read_data("RANKING_RESULTS").set_index("name")
    avg_rank = df["rank_avg"]
    avg_score = df["rpoint_avg"]
    games = df["count"]  # 重み

    # 足切り
    df = df.query("count >= @g.params.stipulated")
    if df.empty:
        m.set_headline(message.random_reply(m, "no_target"), StyleOptions(title=title_text))
        m.status.result = False
        return

    # グラフ生成
    graphutil.setup()
    save_file = textutil.save_file_path("graph.png")

    # 通常の線形回帰
    x_const = sm.add_constant(avg_rank)
    model_ols = sm.OLS(avg_score, x_const).fit()
    a_ols, b_ols = model_ols.params  # 切片と傾き

    # 重み付き線形回帰（WLS）
    model_wls = sm.WLS(avg_score, x_const, weights=games).fit()
    a_wls, b_wls = model_wls.params

    # 残差情報の追加と並び替え
    df["pred_ols"] = model_ols.predict(x_const).round(1)
    df["resid_ols"] = (df["rpoint_avg"] - df["pred_ols"]).round(1)
    df.sort_values("rank_avg", ascending=True, inplace=True)

    #  回帰線の描画用
    x_line = np.linspace(1.0, 4.0, 100)
    y_ols = a_ols + b_ols * x_line
    y_wls = a_wls + b_wls * x_line

    # プロット
    plt.figure(figsize=(8, 6))

    # 散布図（プレイヤー単位で色分け）
    cmap = plt.get_cmap("tab20", len(df))
    player_handles = []
    for i, (name, row) in enumerate(df.iterrows()):
        color = cmap(i)
        plt.scatter(row["rank_avg"], row["rpoint_avg"], s=row["count"] * 2, alpha=0.8, color=color)
        resid_ols = f"{row['resid_ols']:.1f}点".replace("-", "▲")
        player_handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=color,
                markersize=7,
                label=f"{name} : {row['count']}G / {row['rank_avg']:.2f} / {row['rpoint_avg']:.1f}点 / {resid_ols}",
            )
        )

    # 通常回帰線
    (ols_line,) = plt.plot(x_line, y_ols, color="red", label="通常回帰線")

    # 重み付き回帰線
    (wls_line,) = plt.plot(x_line, y_wls, color="blue", linestyle="--", label="重み付き回帰線")

    plt.xlabel("平均順位")
    plt.ylabel("平均素点")
    plt.xlim(0.9, 4.1)
    plt.xticks(np.arange(1.0, 4.1, 0.5))
    plt.gca().invert_xaxis()
    plt.title(f"{title_text} ({game_info.search_start} - {game_info.search_end})")

    # 凡例
    plt.legend(
        title="対戦数 / 平均順位 / 平均素点 / 残差",
        handles=[*player_handles, ols_line, wls_line],
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        borderaxespad=0.0,
        ncol=int(len(df) / 25 + 1),
    )

    plt.grid(True)
    plt.savefig(save_file, bbox_inches="tight")

    m.set_headline(message.header(game_info, m), StyleOptions(title=title_text))
    m.set_message(save_file, StyleOptions(title=title_text, use_comment=True, header_hidden=True))
