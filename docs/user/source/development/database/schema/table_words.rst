.. _table-words:

words
=====

``remarks`` に記録された単語の種別。祝儀や卓外ペナルティなど、ポイントに影響がある単語を登録。\
単語の定義は設定ファイル内の :ref:`regulations-section` で行う。


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
   * - word
     - NOT NULL
     - TEXT
     - ``remarks`` で使用される単語
   * - type
     -
     - INTEGER
     - ``word`` の種別

       :0: 役満扱い
       :1: ワードのカウントのみ
       :2: 卓外ポイント(個人清算)
       :3: 卓外ポイント(チーム清算)
   * - ex_point
     -
     - INTEGER
     - 卓外ポイントとして追加計算されるポイント
   * - rule_version
     -
     - TEXT
     - 使用するルールセット
