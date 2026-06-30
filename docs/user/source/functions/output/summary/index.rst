.. _function-summary:

集計コマンド
============

指定期間内の対象プレイヤー/チームのポイントをそれぞれ集計する。

集計した結果は下記の形式で表示される。

.. toctree::
   :hidden:

   results_details
   results_graph
   results_table_all
   results_table_diff
   winner
   point_transition
   ranking_change
   direct_match


コマンド構文
------------

:チャンネル内呼び出し: <成績集計コマンド> [オプション]
:スラッシュコマンド: /commandname summary [オプション]

.. note::
   ``/commandname`` は以下で定義する

   - `slack-section` の :integrations_section:`slash_command <slack section; slash_command>`
   - `discord-section` の :integrations_section:`slash_command <discord section; slash_command>`


オプション組み合わせ表
----------------------

.. include:: ../../reference_table_legend.inc
.. include:: ../../reference_table_summary.inc


オプション概要
--------------

.. summary:: グラフ

   ポイント集計、順位集計の表を折れ線グラフの表示に切り替える。

.. summary:: 順位

   順位変動、月間生成上位の表示に切り替える。

.. summary:: 比較, 差分, 点差

   通算ポイント集計表を差分形式に切り替える。

.. summary:: 対戦, 対戦結果

   対戦相手とのゲーム結果を表示する。

   - `deliverables-results_details` にゲーム同卓者との結果を追加表示する。
   - ターゲットの複数指定と同時指定で `deliverables-direct_match` を表示する。
