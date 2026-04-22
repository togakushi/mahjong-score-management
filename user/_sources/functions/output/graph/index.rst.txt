.. _function-graph:

グラフ生成
==========

記録された成績データを集計し、グラフで表示する。

構文
----

:チャンネル内呼び出し: <呼び出しキーワード> [オプション]
:スラッシュコマンド: /commandname graph [オプション]

.. note::
   ``/commandname`` は以下で定義する

   - `slack-section` の `slash_command <slash_command_slack>`
   - `discord-section` の `slash_command <slash_command_discord>`


オプション
----------

基本オプション
++++++++++++++

.. mahjong:graph:: メンバー名, チーム名
   :category: 基本オプション

   指定される人数(チーム数)によって出力内容が切り替わる。

   .. list-table::
      :width: 100%
      :widths: 15 20 50
      :header-rows: 1

      * - 指定人数
        - 出力内容
        - 備考
      * - 0名
        - 全体成績グラフ
        - 通算ポイント推移
      * - 1名
        - 個人成績グラフ
        - 統計オプションの追加で回数区切りの統計出力
      * - 2名以上
        - 成績グラフ(比較用)
        - 全体成績グラフから指定メンバーだけに絞り込んで表示


個別オプション
++++++++++++++

.. mahjong:graph:: 順位
   :category: 個別オプション

   グラフのY軸を通算ポイントからゲーム終了時点の順位（ポイント順）に変更する。

   - 全体成績グラフ / 成績グラフ（比較用）でのみ有効


集計オプション
++++++++++++++

.. mahjong:graph:: 日次, デイリー, daily
   :category: 集計オプション

   グラフを日単位で集計する。

.. mahjong:graph:: 週次, ウイークリー, weekly
   :category: 集計オプション

   グラフを週単位で集計する。

.. mahjong:graph:: 月次, マンスリー, monthly
   :category: 集計オプション

   グラフを月単位で集計する。

.. mahjong:graph:: 年次, イヤーリー, yearly
   :category: 集計オプション

   グラフを年単位で集計する。

.. mahjong:graph:: 全体
   :category: 集計オプション

   グラフを指定期間全体で集計する。

   - 強制的に横棒グラフになる


統計出力オプション
++++++++++++++++++

.. mahjong:graph:: 統計
   :category: 統計出力オプション

   指定プレイヤーのゲーム統計情報を出力する。

   - 指定ゲーム数(デフォルト80)区切りで集計

.. mahjong:graph:: 期間, 区間, 区切, 区切り
   :category: 統計出力オプション

   統計指定時の追加オプション

   - 集計で区切るゲーム数の変更
   - 指定例： ``区切200``


共通オプション
++++++++++++++

- `common-options`


出力サンプル
------------

全体成績グラフ詳細
++++++++++++++++++

各メンバーの通算ポイントの推移グラフを出力する。

全員の通算ポイントが1つになる場合は横棒グラフに切り替わる。

.. admonition:: ポイント推移(折れ線グラフ)

   .. compound::

      .. image:: point_line_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: point_line_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)

.. admonition:: 通算ポイント(棒グラフ)

   .. compound::

      .. image:: point_bar_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: point_bar_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)

.. admonition:: 順位変動(折れ線グラフ)

   .. compound:: 日次集約

      .. image:: rank_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: rank_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)


個人成績グラフ詳細
++++++++++++++++++

対象メンバーの以下の成績を出力する。

- ポイントグラフ

  - 獲得ポイント（棒グラフ）
  - 通算ポイント（折れ線グラフ）
  - 平均ポイント（折れ線グラフ）

- 順位グラフ

  - 獲得順位（折れ線グラフ）
  - 平均順位（折れ線グラフ）

統計オプションの追加で指定回数区切りの集計を出力する。

- 獲得ポイント

  - 区間合計
  - 区間平均
  - 通算

- 獲得順位

  - 順位分布
  - 平均順位

- 素点分布（箱ひげ図）
