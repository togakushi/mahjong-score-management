.. index::
   single: メイン設定; 装飾オプション

装飾設定
========

| 使用しない(常に非表示)とする場合はセクションごと省略してよい。
| 使用する場合は省略不可のキーはすべて定義すること。

表示/非表示の設定は `サービス別設定 - 共通設定 <integrations-common>` で行う。


.. _degree-section:

degreeセクション
----------------

対戦数に対して表示される称号。
:integrations_section:`badge_degree` が ``True`` のときに表示される。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 未定義時
     - 備考
   * - .. degree_section:: badge
     - 追加される文字列
     - | 文字列
       | (カンマ区切り)
     - 省略不可(必須)
     - :degree_section:`counter` の数と合わせる
   * - .. degree_section:: counter
     - 称号が変化する対戦数
     - | 数値(int)
       | (カンマ区切り)
     - 省略不可(必須)
     - :degree_section:`badge` の数と合わせる
..
.. code-block:: ini
   :caption: 設定例

   [degree]
   badge = ,:hatching_chick:,:penguin:,:monkey_face:,:skull:,:crown:
   counter = 0,30,60,120,240,480


.. _status-section:

statusセクション
----------------

勝率に対して付く調子バッジ。
:integrations_section:`badge_status` が ``True`` のときに表示される。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 未定義時
     - 備考
   * - .. status_section:: badge
     - 追加される文字列
     - | 文字列
       | (カンマ区切り)
     - 省略不可(必須)
     - 休み、絶不調、不調、普通、好調、絶好調の順に6段階すべて指定
   * - .. status_section:: step
     - 称号が変化する対戦数
     - 数値(float)
     - 省略不可(必須)
     - 普通を基準(勝率50%)として、上下する刻み幅
..
.. code-block:: ini
   :caption: 設定例

   [status]
   badge = :status_oyasumi:,:status_zeffutyou:,:status_futyou:,:status_futuu:,:status_koutyou:,:status_zekkoutyou:
   step = 5.0


.. _grade-section:

gradeセクション
---------------

| `レギュラーメンバー` に対する段位設定（ `ゲストメンバー` には段位を設定できない）。
| :integrations_section:`badge_grade` が ``True`` のときに表示される。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 未定義時
     - 備考
   * - .. grade_section:: table_name
     - 使用する昇段計算テーブルの名前
     - | 文字列
       | (下記参照)
     - 省略不可(必須)
     -
   * - .. grade_section:: guest_title
     - `ゲストメンバー` の段位としてする文字列
     - 文字列
     - 空欄
     -
..

:grade_section:`table_name` に設定する値
   :mahjongsoul / 雀魂: 雀魂風表記
   :tenho / 天鳳: 天鳳風表記
   :その他(JSONファイル名): オリジナル定義ファイルを使用( `gradetable` 参照)

.. code-block:: ini
   :caption: 設定例

   [grade]
   table_name = 天鳳
   guest_title = ***
