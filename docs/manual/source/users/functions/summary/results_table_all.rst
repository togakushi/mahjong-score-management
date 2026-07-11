.. _deliverables-results_table_all:

成績サマリ表（全体）
====================

記録された成績データを集計し、表形式で表示する。

:コマンドタイプ: `function-summary`
:必須オプション: なし
:ターゲット指定: 任意
:個別オプション: なし


オプション
----------

.. flat-table::
   :header-rows: 1
   :width: 100%
   :widths: 10 20 70

   * - 分類
     - 項目
     - 内容
   * - :rspan:`2` 共通オプション
     - | プレイヤー名
       | チーム名
     - | `ターゲット` の指定。
       | 指定プレイヤー/チームに絞り込んで表を生成する。

       .. note:: 単独指定になった場合は `deliverables-results_details` に切り替わる。

   * - 集計範囲指定
     - `date-specification` を参照。
   * - その他のオプション
     - `common-options` を参照。

   * - :rspan:`1` その他オプション
     - :summary:`対戦`
     - ターゲットの指定が複数の場合、 `deliverables-direct_match` に切り替わる。
   * - :summary:`比較` , :summary:`点差` , :summary:`差分`
     - `deliverables-results_table_diff` に切り替わる。


項目説明
--------

通算
   獲得ポイントの合計値。

平均
   獲得ポイントの平均値。

順位分布
   | 獲得した順位の回数と平均順位。
   | 以下の形式で表現される。

   ``1位回数 + 2位回数 + 3位回数 + 4位回数 = トータルゲーム数（平均順位）``

飛
   箱下の回数。


出力サンプル
------------

| メンバー名の指定がない場合、集計期間内で記録されている全メンバーの通算ポイント順に結果を表示する。
| `guest-option` によって集計内容が変わるため、特記には集計条件が記載される。

.. literalinclude:: ../sample/usually.txt
   :caption: 成績サマリ表サンプル（通常表示）
