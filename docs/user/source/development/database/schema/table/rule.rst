.. _table-rule:

rule
====

ルールセット保存テーブル。


内容
----

.. list-table::
   :width: 100%
   :widths: 20 20 10 50
   :header-rows: 1

   * - カラム名
     - 制約
     - 型
     - 内容
   * - rule_version
     - PRIMARY KEY
     - TEXT
     -
   * - mode
     -
     - INTEGER
     -
   * - origin_point
     -
     - INTEGER
     - 配給原点
   * - return_point
     -
     - INTEGER
     - 返し点
   * - rank_point
     -
     - TEXT
     - | 順位点
       | スペースで繋いだ文字列として格納
   * - ignore_flying
     -
     - INTEGER
     - トビの扱い

       :0: ``ignore_flying = False``
       :1: ``ignore_flying = True``
   * - draw_split
     -
     - INTEGER
     - 同着時の順位点の扱い

       :0: ``draw_split = False``
       :1: ``draw_split = True``
   * - undefined_word
     -
     - INTEGER
     - 未定義ワードの扱い
