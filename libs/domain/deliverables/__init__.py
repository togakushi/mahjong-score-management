"""
集計関数

- :doc:`libs.domain.deliverables.detail`: 個人/チーム成績詳細を集計
- :doc:`libs.domain.deliverables.results`: 成績サマリを集計
- :doc:`libs.domain.deliverables.versus`: 直接対戦成績を集計
- :doc:`libs.domain.deliverables.ranking_calc`: ランキングを集計
- :doc:`libs.domain.deliverables.rating_calc`: レーティングを集計
- :doc:`libs.domain.deliverables.score_deviation`: 素点分析表を生成
- :doc:`libs.domain.deliverables.graph_personal`: 個人/チーム/統計グラフを生成
- :doc:`libs.domain.deliverables.graph_rating`: レーティング推移グラフを生成
- :doc:`libs.domain.deliverables.graph_regression`: 平均順位/平均素点の分散図を生成
- :doc:`libs.domain.deliverables.graph_summary`: ポイント推移/順位推移グラフを生成
- :doc:`libs.domain.deliverables.stats_report`: 成績報告書を作成
- :doc:`libs.domain.deliverables.winner`: 月間上位5名の表示
- :doc:`libs.domain.deliverables.matrix`: 直接対戦マトリクスを生成
- :doc:`libs.domain.deliverables.monthly`: 月間成績を集計
- :doc:`libs.domain.deliverables.stats_list`: 個人/チーム成績一覧表を生成
"""

from . import (
    detail,
    graph_personal,
    graph_rating,
    graph_regression,
    graph_summary,
    matrix,
    monthly,
    ranking_calc,
    rating_calc,
    results,
    score_deviation,
    stats_list,
    stats_report,
    versus,
    winner,
)

__all__ = [
    "detail",
    "graph_personal",
    "graph_rating",
    "graph_regression",
    "graph_summary",
    "matrix",
    "monthly",
    "ranking_calc",
    "rating_calc",
    "results",
    "score_deviation",
    "stats_list",
    "stats_report",
    "versus",
    "winner",
]
