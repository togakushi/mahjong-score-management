.. _deliverables-results_list:

成績比較表
==========

比較用の成績一覧表を生成する。

:コマンドタイプ: `function-analysis`
:必須オプション: :analysis:`統計` + :analysis:`グラフ`
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
   * - :rspan:`2` 共通オプション
     - | プレイヤー名
       | チーム名
     - | ターゲットの指定。
       | 指定プレイヤー/チームだけで比較表を生成する。
   * - 集計範囲指定
     - `date-specification` を参照。
   * - その他のオプション
     - `共通オプション <common-options>` を参照。


出力サンプル
------------

.. admonition:: 順位素点相関図

   .. compound::

      .. image:: ../sample/stats_list_team.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)
