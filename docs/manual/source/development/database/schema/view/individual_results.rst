.. index::
   pair: view; individual_results
   :name: view-individual_results

individual_results
==================

ゲーム結果の縦持ちデータ。

1レコードに1人分の成績を持つ。


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
   * - seat
     -
     - 席( ``1`` = 東、``2`` = 南、``3`` = 西、``4`` = 北)
   * - name
     - result.p?_name
     - プレイヤー名
   * - team
     -
     - チーム名
   * - guest
     -
     - ゲストフラグ( ``1`` = ゲスト)
   * - rpoint
     - result.p?_rpoint
     - 素点(数式評価後)
   * - rank
     - result.p?_rank
     - 順位
   * - original_point
     - result.p?_point
     - 獲得ポイント
   * - yakuman
     - regulations.word
     - 役満和了メモ(type = ``0`` のワード)
   * - memo
     - regulations.word
     - その他メモ(type = ``1`` のワード)
   * - regulation
     - regulations.word
     - 個人レギュレーション(type = ``2`` のワード)
   * - ex_point
     - regulations.ex_point
     - 卓外ポイント(個人集計)
   * - point
     - result.p?_point
     - 個人獲得ポイント(卓外ポイント込み)
   * - remarks
     - regulations.word
     - 個人メモすべて(type = ``0`` , ``1`` , ``2`` のワード)
   * - team_regulation
     - regulations.word
     - チームレギュレーション(type = ``2`` , ``3`` のワード)
   * - team_ex_point
     - regulations.ex_point
     - 卓外ポイント(チーム集計)
   * - team_point
     - result.p?_point
     - チーム獲得ポイント(卓外ポイント込み)
   * - team_remarks
     - regulations.word
     - チームメモすべて(type= ``0`` , ``1`` , ``2`` , ``3`` のワード)
   * - collection_daily
     -
     - | 集計対象年月日(YYYY-MM-DD)
       | ``playtime`` から :setting_section:`time_adjust` を引いた日時
   * - rule_version
     - result.rule_version
     - `ルール識別子` を示す文字列
   * - comment
     - result.comment
     - ゲームコメント
   * - mode
     - result.mode
     - 集計モード
