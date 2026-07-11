.. _deliverables-score_chart:

順位素点相関図
==============

「平均順位×平均素点の散布図＋回帰線」の分散図を生成を出力する。

:コマンドタイプ: `function-analysis`
:必須オプション: :analysis:`素点` + :analysis:`グラフ`
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
     - | `ターゲット` の指定。
       | 指定プレイヤー/チームだけで分散図を生成する。
   * - 集計範囲指定
     - `date-specification` を参照。
   * - その他のオプション
     - `common-options` を参照。


項目説明
--------

対戦数
    集計範囲内で集計対象になったゲーム数

平均順位
    集計対象ゲームの平均順位

平均素点
    集計対象ゲームの平均素点

残差
    平均素点と回帰線との差分

通常回帰線
    平均順位に対する平均素点の期待値

重み付き回帰線
    対戦数に重みをつけて計算した回帰線


出力サンプル
------------

.. admonition:: 順位素点相関図

   .. compound::

      .. image:: ../sample/regression_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: ../sample/regression_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)
