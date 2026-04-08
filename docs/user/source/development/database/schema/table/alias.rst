.. _table-alias:

alias
=====

メンバーの別名を管理するテーブル。

| Python側で *{ name: member }* という辞書を生成するのに利用される。
| 別名ではないメンバー名も *name* に存在する。


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
   * - name
     - PRIMARY KEY
     - TEXT
     - 別名(ニックネーム)
   * - member
     - NOT NULL
     - TEXT
     - プレイヤー名
