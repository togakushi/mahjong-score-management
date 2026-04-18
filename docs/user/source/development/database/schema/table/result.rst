.. index::
   pair: table; result
   :name: table-result

result
======

ポストされたデータを管理するテーブル。*p1* ～ *p4* は東家～北家を表している。

| *p?_str* に素点の情報（文字列、記号があるものはそのまま）が記録される。
| *p?_str* の式を評価した値は *p?_rpoint* に、素点から計算した獲得ポイントと順位が *p?_point* 、 *p?_rank* に記録される。

ポイント計算などはPython側で処理し、その結果を記録する。リレーションなどはない。


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
   * - ts
     - PRIMARY KEY
     - TEXT
     - ゲーム結果が記録された時間
   * - playtime
     - UNIQUE
     - TIMESTAMP
     - タイムスタンプ(tsを変換)
   * - p1_name
     - NOT NULL
     - TEXT
     - 東家プレイヤー名
   * - p1_str
     - NOT NULL
     - TEXT
     - 入力された東家の素点
   * - p1_rpoint
     -
     - INTEGER
     - 東家素点(計算後)
   * - p1_rank
     -
     - INTEGER
     - 東家順位
   * - p1_point
     -
     - INTEGER
     - 東家が獲得したポイント
   * - p2_name
     - NOT NULL
     - TEXT
     - 南家プレイヤー名
   * - p2_str
     - NOT NULL
     - TEXT
     - 入力された南家の素点
   * - p2_rpoint
     -
     - INTEGER
     - 南家素点(計算後)
   * - p2_rank
     -
     - INTEGER
     - 南家順位
   * - p2_point
     -
     - INTEGER
     - 南家が獲得したポイント
   * - p3_name
     - NOT NULL
     - TEXT
     - 西家プレイヤー名
   * - p3_str
     - NOT NULL
     - TEXT
     - 入力された西家の素点
   * - p3_rpoint
     -
     - INTEGER
     - 西家素点(計算後)
   * - p3_rank
     -
     - INTEGER
     - 西家順位
   * - p3_point
     -
     - INTEGER
     - 西家が獲得したポイント
   * - p4_name
     - NOT NULL
     - TEXT
     - 北家プレイヤー名
   * - p4_str
     - NOT NULL
     - TEXT
     - 入力された北家の素点
   * - p4_rpoint
     -
     - INTEGER
     - 北家素点(計算後)
   * - p4_rank
     -
     - INTEGER
     - 北家順位
   * - p4_point
     -
     - INTEGER
     - 北家が獲得したポイント


   * - deposit
     -
     - INTEGER
     - 供託(配給原点と素点合計の差分)
   * - rule_version
     -
     - TEXT
     - *ルール識別子* を示す文字列
   * - comment
     -
     - TEXT
     - ゲームコメント
   * - source
     -
     - TEXT
     - スコア入力元識別子
   * - mode
     -
     - INTEGER
     - 集計モード
