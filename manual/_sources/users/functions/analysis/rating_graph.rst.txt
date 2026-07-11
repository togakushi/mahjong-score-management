.. _deliverables-rating_graph:

レーティング推移グラフ
======================

記録された成績データを集計し、レーティングの推移グラフを生成する。

:コマンドタイプ: `function-analysis`
:必須オプション: :analysis:`レート` or :analysis:`レーティング` + :analysis:`グラフ`
:ターゲット指定: 任意
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
     - | `ターゲット` の指定。
       | 指定プレイヤー/チームだけでレーティング推移グラフを生成する。
   * - 集計範囲指定
     - `date-specification` を参照。
   * - グラフ集約オプション
     - `grouping-options` を参照。
   * - その他のオプション
     - `common-options` を参照。


出力サンプル
------------

.. admonition:: レーティング推移グラフ

   .. compound::

      .. image:: ../sample/rating_graph_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: ../sample/rating_graph_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)
