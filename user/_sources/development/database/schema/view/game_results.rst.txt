.. _view-game_results:

game_results
============

ゲーム結果の横持ちデータ。

1レコードに1ゲーム分の結果(4人分の成績)を持つ。


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
   * - p1_name
     - result.p1_name
     - 東家プレイヤー名
   * - p1_team
     - team.name
     - 東家所属チーム名
   * - p1_guest
     -
     - 東家ゲストフラグ( ``1`` = ゲスト)
   * - p1_rpoint
     - result.p1_rpoint
     - 東家素点(計算後)
   * - p1_rank
     - result.p1_rank
     - 東家順位
   * - p1_original
     - result.p1_point
     - 東家が獲得した個人ポイント
   * - p1_regulation
     - regulations.word
     - 東家個人レギュレーション(type = ``2`` のワード)
   * - p1_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(個人集計)
   * - p1_point
     - result.p1_point
     - 東家が獲得した個人ポイント(卓外ポイントを含む)
   * - t1_regulation
     - regulations.word
     - 東家チームレギュレーション(type = ``2`` , ``3`` のワード)
   * - t1_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(チーム集計)
   * - t1_point
     - result.p1_point
     - 東家が獲得したチームポイント(卓外ポイントを含む)
   * - p1_yakuman
     - regulations.word
     - 役満和了メモ(type = ``0`` のワード)
   * - p1_memo
     - regulations.word
     - その他メモ(type = ``1`` のワード)
   * - p1_remarks
     - regulations.word
     - 個人メモすべて(type = ``0`` , ``1`` , ``2`` のワード)
   * - t1_remarks
     - regulations.word
     - チームメモすべて(type = ``0`` , ``1`` , ``2`` , ``3`` のワード)
   * - p2_name
     - result.p2_name
     - 南家プレイヤー名
   * - p2_team
     - team.name
     - 南家所属チーム名
   * - p2_guest
     -
     - 南家ゲストフラグ( ``1`` = ゲスト)
   * - p2_rpoint
     - result.p2_rpoint
     - 南家素点(計算後)
   * - p2_rank
     - result.p2_rank
     - 南家順位
   * - p2_original
     - result.p2_point
     - 南家が獲得した個人ポイント
   * - p2_regulation
     - regulations.word
     - 南家個人レギュレーション(type = ``2`` のワード)
   * - p2_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(個人集計)
   * - p2_point
     - result.p2_point
     - 南家が獲得した個人ポイント(卓外ポイントを含む)
   * - t2_regulation
     - regulations.word
     - 南家チームレギュレーション(type = ``2`` , ``3`` のワード)
   * - t2_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(チーム集計)
   * - t2_point
     - result.p2_point
     - 南家が獲得したチームポイント(卓外ポイントを含む)
   * - p2_yakuman
     - regulations.word
     - 役満和了メモ(type = ``0`` のワード)
   * - p2_memo
     - regulations.word
     - その他メモ(type = ``1`` のワード)
   * - p2_remarks
     - regulations.word
     - 個人メモすべて(type = ``0`` , ``1`` , ``2`` のワード)
   * - t2_remarks
     - regulations.word
     - チームメモすべて(type = ``0`` , ``1`` , ``2`` , ``3`` のワード)
   * - p3_name
     - result.p3_name
     - 西家プレイヤー名
   * - p3_team
     - team.name
     - 西家所属チーム名
   * - p3_guest
     -
     - 西家ゲストフラグ( ``1`` = ゲスト)
   * - p3_rpoint
     - result.p3_rpoint
     - 西家素点(計算後)
   * - p3_rank
     - result.p3_rank
     - 西家順位
   * - p3_original
     - result.p3_point
     - 西家が獲得した個人ポイント
   * - p3_regulation
     - regulations.word
     - 西家個人レギュレーション(type = ``2`` のワード)
   * - p3_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(個人集計)
   * - p3_point
     - result.p3_point
     - 西家が獲得した個人ポイント(卓外ポイントを含む)
   * - t3_regulation
     - regulations.word
     - 西家チームレギュレーション(type = ``2`` , ``3`` のワード)
   * - t3_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(チーム集計)
   * - t3_point
     - result.p3_point
     - 西家が獲得したチームポイント(卓外ポイントを含む)
   * - p3_yakuman
     - regulations.word
     - 役満和了メモ(type = ``0`` のワード)
   * - p3_memo
     - regulations.word
     - その他メモ(type = ``1`` のワード)
   * - p3_remarks
     - regulations.word
     - 個人メモすべて(type = ``0`` , ``1`` , ``2`` のワード)
   * - t3_remarks
     - regulations.word
     - チームメモすべて(type = ``0`` , ``1`` , ``2`` , ``3`` のワード)
   * - p4_name
     - result.p4_name
     - 北家プレイヤー名
   * - p4_team
     - team.name
     - 北家所属チーム名
   * - p4_guest
     -
     - 北家ゲストフラグ( ``1`` = ゲスト)
   * - p4_rpoint
     - result.p4_rpoint
     - 北家素点(計算後)
   * - p4_rank
     - result.p4_rank
     - 北家順位
   * - p4_original
     - result.p4_point
     - 北家が獲得した個人ポイント
   * - p4_regulation
     - regulations.word
     - 北家個人レギュレーション(type = ``2`` のワード)
   * - p4_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(個人集計)
   * - p4_point
     - result.p4_point
     - 北家が獲得した個人ポイント(卓外ポイントを含む)
   * - t4_regulation
     - regulations.word
     - 北家チームレギュレーション(type = ``2`` , ``3`` のワード)
   * - t4_ex_point
     - regulations.ex_point
     - 卓外ポイントの合計値(チーム集計)
   * - t4_point
     - result.p4_point
     - 北家が獲得したチームポイント(卓外ポイントを含む)
   * - p4_yakuman
     - regulations.word
     - 役満和了メモ(type = ``0`` のワード)
   * - p4_memo
     - regulations.word
     - その他メモ(type = ``1`` のワード)
   * - p4_remarks
     - regulations.word
     - 個人メモすべて(type = ``0`` , ``1`` , ``2`` のワード)
   * - t4_remarks
     - regulations.word
     - チームメモすべて(type = ``0`` , ``1`` , ``2`` , ``3`` のワード)
   * - deposit
     -
     - 供託
   * - collection_daily
     -
     - 集計対象年月日(YYYY-MM-DD)
   * - comment
     - result.comment
     - コメント
   * - guest_count
     -
     - ゲーム内のゲストの合計人数
   * - same_team
     -
     - ``1`` = チーム同卓あり
   * - rule_version
     - result.rule_version
     - *ルール識別子* を示す文字列
   * - mode
     - result.mode
     - 集計モード
