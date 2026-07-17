.. index::
   single: メイン設定; 装飾オプション

装飾設定
========

| 使用しない(常に非表示)とする場合はセクションごと省略してよい。
| デフォルト値は持たないため、設定時はすべてのキーの設定が必要になる。


.. _degree-section:

degreeセクション
----------------

| 対戦数に対して表示される称号。
| 表示/非表示の設定は `integrations-common` で行う。

.. list-table::
   :width: 100%
   :widths: 10 20 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 備考
   * - .. degree_section:: badge
     - 追加される文字列
     - | 文字列
       | (カンマ区切り)
     - :degree_section:`counter` の数と合わせる
   * - .. degree_section:: counter
     - 称号が変化する対戦数
     - | 数値(int)
       | (カンマ区切り)
     - :degree_section:`badge` の数と合わせる
..


.. _status-section:

statusセクション
----------------

| 勝率に対して付く調子バッジ。
| 表示/非表示の設定は `integrations-common` で行う。

.. list-table::
   :width: 100%
   :widths: 10 20 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 備考
   * - .. status_section:: badge
     - 追加される文字列
     - | 文字列
       | (カンマ区切り)
     - 休み、絶不調、不調、普通、好調、絶好調の順に6段階すべて指定
   * - .. status_section:: step
     - 称号が変化する対戦数
     - 数値(float)
     - 普通を基準(勝率50%)として、上下する刻み幅
..


.. _grade-section:

gradeセクション
---------------

| `レギュラーメンバー` に対する段位設定。
| 表示/非表示の設定は `integrations-common` で行う。

.. list-table::
   :width: 100%
   :widths: 10 20 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 備考
   * - .. grade_section:: table_name
     - 使用する昇段計算テーブルの名前
     - 文字列(備考参照)
     - :mahjongsoul / 雀魂: 雀魂風表記
       :tenho / 天鳳: 天鳳風表記
       :その他(JSONファイル名): オリジナル定義ファイルを使用( `gradetable` 参照)
..
.. caution:: `ゲストメンバー` には段位を設定できない。
