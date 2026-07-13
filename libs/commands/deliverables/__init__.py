"""
集計関数

- :doc:`libs.commands.deliverables.results_detail`: 個人/チーム成績詳細を集計
- :doc:`libs.commands.deliverables.results_summary`: 成績サマリを集計
- :doc:`libs.commands.deliverables.versus`: 直接対戦成績を集計
- :doc:`libs.commands.deliverables.ranking_calc`: ランキングを集計
- :doc:`libs.commands.deliverables.rating_calc`: レーティングを集計
- :doc:`libs.commands.deliverables.score_deviation`: 素点分析表を生成
- :doc:`libs.commands.deliverables.graph_personal`: 個人/チーム/統計グラフを生成
- :doc:`libs.commands.deliverables.graph_rating`: レーティング推移グラフを生成
- :doc:`libs.commands.deliverables.graph_regression`: 平均順位/平均素点の分散図を生成
- :doc:`libs.commands.deliverables.graph_summary`: ポイント推移/順位推移グラフを生成
- :doc:`libs.commands.deliverables.winner`: 月間上位5名の表示
- :doc:`libs.commands.deliverables.matrix`: 直接対戦マトリクスを生成
- :doc:`libs.commands.deliverables.game_statistics`: ゲーム統計情報を集計
- :doc:`libs.commands.deliverables.stats_report`: 成績報告書を作成
- :doc:`libs.commands.deliverables.text_assembly`: メッセージテキストの組み立て
"""

from . import (
    game_statistics,
    graph_personal,
    graph_rating,
    graph_regression,
    graph_summary,
    matrix,
    ranking_calc,
    rating_calc,
    results_detail,
    results_summary,
    score_deviation,
    stats_report,
    text_assembly,
    versus,
    winner,
)

__all__ = [
    "game_statistics",
    "graph_personal",
    "graph_rating",
    "graph_regression",
    "graph_summary",
    "matrix",
    "ranking_calc",
    "rating_calc",
    "results_detail",
    "results_summary",
    "score_deviation",
    "stats_report",
    "text_assembly",
    "versus",
    "winner",
]
