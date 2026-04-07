member
======

成績などで表示されるメンバーを管理するテーブル。

| 便宜上 *id* を主キーとしているが、リレーションはない。
| *id=0* はゲストで使用される。


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
     -
   * - name
     - NOT NULL
     - TEXT
     - プレイヤー名
   * - slack_id
     -
     - TEXT
     - 未使用
   * - team_id
     -
     - INTEGER
     - 所属チームID
   * - flying
     -
     - INTEGER
     - 拡張用フラグ(未使用)
   * - reward
     -
     - INTEGER
     - 拡張用フラグ(未使用)
   * - abuse
     -
     - INTEGER
     - 拡張用フラグ(未使用)
