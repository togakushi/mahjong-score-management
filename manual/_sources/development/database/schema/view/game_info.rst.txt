.. index::
   pair: view; team
   :name: view-game_info

game_info
=========

内容
----

.. list-table::
   :width: 100%
   :widths: 20 30 50
   :header-rows: 1

   * - カラム名
     - 参照元
     - 内容
   * - playtime
     -
     - タイムスタンプ(tsを変換)
   * - ts
     - result.ts
     - ゲーム結果が記録された時間
   * - guest_count
     -
     - ゲーム内のゲストの人数
   * - same_team
     -
     - ゲーム内に同じチームのメンバーが存在すれば ``1``
   * - rule_version
     - result.rule_version
     - *ルール識別子* を示す文字列
   * - comment
     - result.comment
     - ゲームコメント
   * - mode
     - result.mode
     - 集計モード
