.. _function-analysis:

分析コマンド
============

ポイント以外の情報を用いての成績分析、他プレイヤー/チームとの成績比較を行う。

.. toctree::
   :hidden:

   ranking
   rating_table
   rating_graph
   matchup_matrix
   score_analysis
   score_chart
   results_comparison
   results_report
   results_analysis
   results_list


コマンド構文
------------

:チャンネル内呼び出し: <分析コマンド> [`ターゲット`] [`オプション`]

   .. note:: ``分析コマンド`` は以下で定義される

      - `analysis セクション <results_management>` の :sub_commands_section:`commandword`

:スラッシュコマンド: /commandname analysis [`ターゲット`] [`オプション`]

   .. note:: ``/commandname`` は以下で定義される

      - `slack-section` の :integrations_section:`slash_command <slack section; slash_command>`
      - `discord-section` の :integrations_section:`slash_command <discord section; slash_command>`


オプション組み合わせ表
----------------------

.. include:: ../../reference_table_legend.inc
.. include:: ../../reference_table_analysis.inc


オプション概要
--------------

.. analysis:: グラフ

   グラフ表記に切り替える。

.. analysis:: レポート

   成績詳細レポートを生成する。

.. analysis:: レート, レーティング

   レーティングを集計。

.. analysis:: 対戦, 対戦結果

   `deliverables-matchup_matrix` の表示。

.. analysis:: 統計

   各プレイヤー/チームの成績比較。

.. analysis:: 素点

   ゲーム終了時点の素点情報を基にした成績の分析を行う。
