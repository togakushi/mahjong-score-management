.. _rule-set:

ルールセット定義
================

.. list-table::
   :width: 100%
   :widths: 15 20 15 30 50
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 省略時
     - 備考
   * - .. rule_set_section:: rule_version
     - ルール識別子
     - 文字列
     - - `main-config` 内の `mahjong-section`

         - 省略不可

       - `rule-config` 内の `ルールセット`

         - セクション名を `rule_version` として扱う
     - `mahjong-section` の `rule_version` が未定義の場合、 `mahjong-section` のパラメータはすべて無視される
   * - .. rule_set_section:: mode
     - 集計モード
     - 数値(3 or 4)
     - 4
     - 四人打ち/三人打ちの指定
   * - .. rule_set_section:: point
     - 配給原点
     - 数値(100点単位)
     - :mode=4: 250
       :mode=3: 350
     -
   * - .. rule_set_section:: return
     - 返し点
     - 数値(100点単位)
     - :mode=4: 300
       :mode=3: 400
     - 清算時の基準点(返し点-配給原点x人数がオカとなる)
   * - .. rule_set_section:: rank_point
     - 順位点
     - | カンマ区切り
       | 数値(1000点単位)
     - :mode=4: 30, 10, -10, -30
       :mode=3: 30, 0, -30
     - 1位から順に並べる(必要以上の列挙は無視される)
   * - .. rule_set_section:: ignore_flying
     - 箱下のカウント表示
     - 真偽値
     - False
     - :True: トビ終了の表示をなくす
   * - .. rule_set_section:: draw_split
     - 順位点の山分け
     - 真偽値
     - False
     - :True: 素点同点時に順位点を山分けする（同点者の順位は同じになる）
       :False: 席順で順位を決定し、順位点を決める
   * - .. rule_set_section:: undefined_word
     - 未定義ワードタイプ
     - 数値(int)
     - 1
     - `regulations-section` で使用
   * - .. rule_set_section:: keywords
     - 成績記録キーワード
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - `keywords` が空欄の `ルールセット` は参照専用となる
   * - .. rule_set_section:: remarks
     - メモ記録ワード
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - `default-behavior` 参照
   * - .. rule_set_section:: dropitems
     - 非表示にする項目を指定
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - カンマ区切りで複数指定可

..

| セクション内のキーが省略された場合はDEFAULTセクションに定義している値がセットされる。
| DEFAULTセクションでの定義がない場合は上記表の通りとなる。



`rule-config` 内の `ルールセット` で定義する `rule_version` が省略されている場合はセクション名が `rule_version` として登録される。

.. important::
   セクション名及びキー名の半角英字はすべて小文字として扱われる。


.. _default-behavior:

メモ記録ワード省略時の挙動
----------------------------

`remarks` の定義が省略された場合、 `setting-section` の `remarks_suffix` の設定の有無で登録される内容が変化する。

.. list-table::
   :width: 100%
   :widths: 15 15 50
   :header-rows: 1

   * - remarks
     - remarks_suffix
     - 登録内容
   * - |:x:|
     - |:x:|
     - 何も登録されない
   * - |:o:|
     - |:x:|
     - `remarks` の内容が登録される
   * - |:x:|
     - |:o:|
     - `keywords` をプレフィックス、 `remarks_suffix` をサフィックスとした組み合わせが登録される
   * - |:o:|
     - |:o:|
     - `remarks` の内容が登録される
