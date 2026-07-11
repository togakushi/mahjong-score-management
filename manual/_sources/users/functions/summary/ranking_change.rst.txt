.. _deliverables-ranking_change:

順位変動グラフ
==============

順位（通算ポイント順）の変化をグラフで表示する。

:コマンドタイプ: `function-summary`
:必須オプション: :summary:`グラフ` + :summary:`順位`
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
   * - 集計範囲指定
     - `date-specification` を参照。
   * - 集約オプション
     - `grouping-options` を参照。
   * - その他のオプション
     - `common-options` を参照。


出力サンプル
------------

.. admonition:: 順位変動(折れ線グラフ)

   .. compound:: 日次集約

      .. image:: ../sample/rank_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: ../sample/rank_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)
