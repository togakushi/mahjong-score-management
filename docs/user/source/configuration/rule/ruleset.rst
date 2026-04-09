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
   * - :index:`rule_version <pair: rule_set section; rule_version>`
     - ルール識別子
     - 文字列
     - `undefined-behavior` 参照
     -
   * - :index:`mode <pair: rule_set section; mode>`
     - 集計モード
     - 数値(3 or 4)
     - 4
     - 四人打ち/三人打ちの指定
   * - :index:`point <pair: rule_set section; point>`
     - 配給原点
     - 数値(100点単位)
     - :mode=4: 250
       :mode=3: 350
     -
   * - :index:`return <pair: rule_set section; return>`
     - 返し点
     - 数値(100点単位)
     - :mode=4: 300
       :mode=3: 400
     - 清算時の基準点(返し点-配給原点x人数がオカとなる)
   * - :index:`rank_point <pair: rule_set section; rank_point>`
     - 順位点
     - | カンマ区切り
       | 数値(1000点単位)
     - :mode=4: 30, 10, -10, -30
       :mode=3: 30, 0, -30
     - 1位から順に並べる(必要以上の列挙は無視される)
   * - :index:`ignore_flying <pair: rule_set section; ignore_flying>`
     - 箱下のカウント表示
     - 真偽値
     - False
     - ``True`` : トビ終了の表示をなくす
   * - :index:`draw_split <pair: rule_set section; draw_split>`
     - 順位点の山分け
     - 真偽値
     - False
     - ``True`` : 素点同点時に順位点を山分けする
   * - :index:`undefined_word <pair: rule_set section; undefined_word>`
     - 未定義ワードタイプ
     - 数値(int)
     - 1
     - `regulations-section` で使用
   * - :index:`keywords <pair: rule_set section; keywords>`
     - 成績記録キーワード
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - ``keywords`` が空欄のルールセットは参照専用となる
   * - :index:`remarks <pair: rule_set section; remarks>`
     - メモ記録用ワード
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - [メモ記録用ワード省略時の挙動](#メモ記録用ワード省略時の挙動)参照
   * - :index:`dropitems <pair: rule_set section; dropitems>`
     - 非表示にする項目を指定
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - カンマ区切りで複数指定可

| セクション内のキーが省略された場合はDEFAULTセクションに定義している値がセットされる。
| DEFAULTセクションでの定義がない場合は上記表の通りとなる。


.. _undefined-behavior:

ルール識別子省略時の挙動
------------------------

メイン設定ファイル内の「 `mahjong-section` 」

   | ``rule_version`` は必須パラメータとなる。
   | ``rule_version`` が存在しない場合、セクション内のパラメータはすべて無視される。

ルールセット定義ファイル内のルールセット

   ``rule_version`` が省略されている場合はセクション名が ``rule_version`` として登録される。

.. important::
   セクション名及びキー名の半角英字はすべて小文字として扱われる。


メモ記録用ワード省略時の挙動
----------------------------

``remarks`` の定義が省略された場合、 `setting-section` の ``remarks_suffix`` の設定の有無で登録される内容が変化する。

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
     - ``remarks`` の内容が登録される
   * - |:x:|
     - |:o:|
     - ``keywords`` をプレフィックス、 ``remarks_suffix`` をサフィックスとした組み合わせが登録される
   * - |:o:|
     - |:o:|
     - ``remarks`` の内容が登録される
