.. index::
   pair: view; regulations
   :name: view-regulations

regulations
===========

``remarks`` の情報を集約。


内容
----

.. list-table::
   :width: 100%
   :widths: 20 30 50
   :header-rows: 1

   * - カラム名
     - 参照元
     - 内容
   * - thread_ts
     - remarks.thread_ts
     - 対象のゲームのタイムスタンプ
   * - name
     - remarks.name
     - 記録対象プレイヤー名
   * - team
     - team.name
     - 記録対象チーム名
   * - guest
     -
     - ゲストフラグ( ``1`` = ゲスト)
   * - word
     - remarks.matter
     - 内容(複数レコードある場合はカンマ区切りで連結される)
   * - count
     -
     - 1レコードに集約された ``matter`` の個数
   * - type
     - words.type
     - ``remarks`` の種別
   * - ex_point
     - words.ex_point
     - 追加計算されるポイント合計(卓外ポイント合計値)
