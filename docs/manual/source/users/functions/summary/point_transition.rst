
.. _deliverables-point_transition:

通算ポイント推移グラフ
======================

通算ポイントの変化をグラフで表示する。

:コマンドタイプ: `function-summary`
:必須オプション: :summary:`グラフ`
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
       | 指定プレイヤー/チームに絞ってグラフを生成する。

       .. note:: 単独指定時は `deliverables-results_graph` に切り替わる。

   * - 集計範囲指定
     - `date-specification` を参照。
   * - 集約オプション
     - `grouping-options` を参照。
   * - その他のオプション
     - `common-options` を参照。


出力サンプル
------------

集約時に全員の通算ポイントが1つになる場合は横棒グラフに切り替わる。

.. admonition:: ポイント推移(折れ線グラフ)

   .. compound::

      .. image:: ../sample/point_line_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: ../sample/point_line_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)

.. admonition:: 通算ポイント(棒グラフ)

   .. compound::

      .. image:: ../sample/point_bar_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: ../sample/point_bar_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)
