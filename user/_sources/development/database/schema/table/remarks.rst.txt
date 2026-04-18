.. index::
   pair: table; remarks
   :name: table-remarks

remarks
=======

ゲーム結果に対して残すメモを記録するテーブル。


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
   * - thread_ts
     - NOT NULL
     - TEXT
     - ゲーム結果が記録された時間
   * - event_ts
     - NOT NULL
     - TEXT
     - メモが記録された時間
   * - name
     - NOT NULL
     - TEXT
     - メモ内容(誰が)
   * - matter
     - NOT NULL
     - TEXT
     - メモ内容(何をした)
