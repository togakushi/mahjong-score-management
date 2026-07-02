非表示項目設定
==============

| 指定したキーワードに該当する項目を出力される集計結果の表示から削除する設定。
| 指定できるキーワードは、出力される情報の墨付き括弧内の見出し、各表の項目となり、該当しないキーワードは無視される。

非表示項目の定義は以下で行う。

- `main-config` の :sub_commands_section:`dropitems`

  - ``summary`` / ``analysis`` / ``help`` の各セクション

- `rule-set` の :rule_set_section:`dropitems`

  - `main-config` の :sub_commands_section:`dropitems` の定義に追加


自動で追加される非表示項目
--------------------------

設定内容や関連ワードに含まれるワードが指定されている場合、その関連ワードが非表示項目に追加される。

.. describe:: 設定状況によって追加されるワード

   - `ignore_flying` が ``True`` の場合、:rule_set_section:`dropitems` に「トビ」を追加

.. describe:: トビ関連ワード

   - トビ
   - トビ率

.. describe:: 役満関連ワード

   - 役満
   - 役満和了
   - 役満和了率

.. describe:: レギュレーション関連ワード

   - 卓外
   - 卓外清算
   - 卓外ポイント

.. describe:: その他のワード

   - その他
   - メモ
