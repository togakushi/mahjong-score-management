.. index::
   single: メイン設定; ルール定義

ルール定義
==========

.. index::
   pair: メイン設定; mahjong section
   :name: mahjong-section

mahjongセクション
-----------------

| `ルールセット` を定義するセクション。
| 設定可能なパラメータは `rule-set` を参照。

このセクションに `rule_version` が含まれない場合は、 `ルールセット` として扱われない。

`mahjong-section` はオプション扱いのセクションであり、省略可能となる。


.. index::
   single: メイン設定; マッピング定義
   single: ルールセット; マッピング定義

マッピング定義
==============

| ゲーム結果の登録時に用いられる *成績記録キーワード* と *ルール識別子* はマッピングテーブルによって紐付けられる。
| `rule-set` で定義した `keywords` と `rule_version` の組み合わせでマッピングが生成されるが、 `keyword_mapping-section` で自由に組み合わせを追加できる。

`keywords` の定義がない `ルールセット` はマッピングテーブルに存在しないため、記録に用いることができない。

.. tip::
   | `keywords` は複数定義できるので、マッピングテーブルに追加するだけなら `keywords` を増やせばよい。
   | `keyword_mapping-section` で追加した *成績記録キーワード* は `function-call-keyword` に使用されない。


.. index::
   pair: メイン設定; keyword_mapping section
   :name: keyword_mapping-section

keyword_mappingセクション
-------------------------

*成績記録キーワード* と *ルール識別子* を紐付ける。

keyword_mappingセクションはオプション扱いのセクションであり、省略可能となる。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - <任意のキーワード>
     - 成績記録キーワード
     - 文字列(ルール識別子)
     -
     - 未定義の *ルール識別子* は登録対象外となる

（参考）設定例
++++++++++++++

.. code-block:: ini
   :caption: ルールセットの設定例

   [M-league]
   mode = 4
   origin_point = 250
   return_point = 300
   rank_point = 30, 10, -10, -30
   draw_split = True
   ignore_flying = True
   keywords = リーグルール

.. code-block:: ini
   :caption: マッピングの設定例

   [keyword_mapping]
   新しい成績記録キーワード = M-league
