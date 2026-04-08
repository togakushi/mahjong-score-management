.. _table-team:

team
====

チーム名を管理するテーブル。


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
   * - id
     - PRIMARY KEY
     - INTEGER
     - チームID
   * - name
     - NOT NULL, UNIQUE
     - TEXT
     - チーム名
