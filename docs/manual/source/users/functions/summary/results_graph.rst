.. _deliverables-results_graph:

成績グラフ
==========

指定プレイヤー/チームの獲得ポイント、獲得順位をグラフ化する。

:コマンドタイプ: `function-summary`
:必須オプション: :summary:`グラフ`
:ターゲット指定: 単独
:個別オプション: なし


オプション
----------

.. flat-table::
   :header-rows: 1
   :width: 100%
   :widths: 10 20 70

   * - 分類
     - 項目
     - 内容
   * - :rspan:`3` 共通オプション
     - | プレイヤー名
       | チーム名
     - | `ターゲット` の指定（単独）。
       | 指定プレイヤー/チームの成績を集計する。
   * - 集計範囲指定
     - `date-specification` を参照。
   * - 集約オプション
     - `grouping-options` を参照。
   * - その他のオプション
     - `common-options` を参照。


項目説明
--------

.. describe:: グラフ内容

   ポイントグラフ

   - 獲得ポイント（棒グラフ）
   - 通算ポイント（折れ線グラフ）
   - 平均ポイント（折れ線グラフ）

   順位グラフ

   - 獲得順位（折れ線グラフ）
   - 平均順位（折れ線グラフ）


出力サンプル
------------

.. admonition:: 成績グラフ

   .. compound::

      .. image:: ../sample/results_graph_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: ../sample/results_graph_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)
