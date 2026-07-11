.. _deliverables-score_analysis:

素点分析
========

各着順獲得時の素点状況を分析する。

:コマンドタイプ: `function-analysis`
:必須オプション: :analysis:`素点`
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
       | 指定プレイヤー/チームだけで表を生成する。
   * - 集計範囲指定
     - `date-specification` を参照。
   * - その他のオプション
     - `common-options` を参照。


項目説明
--------

平均素点
   ゲーム終了時点の素点平均

x位偏差
   | x位の全体平均素点と集計対象の平均素点の差分
   | x位偏差 = 集計対象のx位平均素点 - 全体のx位平均素点


出力サンプル
------------

.. literalinclude:: ../sample/score_analysis.txt
   :caption: 素点分析
