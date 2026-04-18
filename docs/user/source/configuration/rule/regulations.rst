.. index::
   single: ルールセット; レギュレーション設定

レギュレーション設定
====================

ゲーム結果とは別清算されるレギュレーションを設定する。

| 通算ポイントに対し指定されたポイントのボーナスまたはペナルティが加えられる。
| レギュレーション設定のセクション定義が見つからない場合は何も設定されず、 `undefined_word <undefined_word>` のみの動作となる。

レギュレーションの記録は `remarks_record` で行う。


.. index::
   single: ルールセット; 個人清算レギュレーション

個人清算レギュレーション
------------------------

| 個人成績出力時に清算されるポイントを定義する。
| チーム成績はチームメンバー全員の個人成績の総和となるため、チーム成績にも影響がある。


.. _regulations-section:

regulationsセクション
+++++++++++++++++++++

定義されているキーが `table-words` テーブルの ``word`` として事前登録される。

| ``yakuman_list`` 及び ``word_list`` にはカンマで区切られたワードを並べる。
| テーブルに登録されていないワードが使用された場合、そのワードのtypeは `undefined_word <undefined_word>` で指定した値となる。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - yakuman_list
     - 事前登録ワード(役満)
     - 文字列(カンマ区切り)
     - None
     - 事前登録ワードを ``type=0`` として登録
   * - word_list
     - 事前登録ワード(個別)
     - 文字列(カンマ区切り)
     - None
     - 事前登録ワードを ``type=1`` として登録
   * - その他（任意のワード）
     - 卓外清算(個人)として登録される事前登録ワード
     - 数値(追加計算される卓外ポイント)
     -
     - | キーで定義した単語を ``type=2`` として登録
       | ポイントは1000点単位


.. index::
   single: ルールセット; チーム清算レギュレーション

チーム清算レギュレーション
--------------------------

| チーム成績出力時に清算されるポイントを定義する。
| チームに対する清算のため、個人成績には影響はない。


.. _regulations_team-section:

regulations_teamセクション
++++++++++++++++++++++++++

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - 任意のワード
     - 卓外清算(チーム)として登録される事前登録ワード
     - 数値(追加計算される卓外ポイント)
     -
     - | キーで定義した単語を ``type=3`` として登録
       | ポイントは1000点単位


レギュレーション設定例
----------------------

.. code-block:: ini
   :caption: 卓外清算の設定例

   [regulations]
   役満祝儀 = 10
   卓外ペナルティ = -20

   [regulations_team]
   遅刻 = -100

.. important::
   INIファイルの仕様上、セクション名及びキー名の半角英字はすべて小文字として扱われる。


ルールセット個別レギュレーション設定
====================================

複数の `ルールセット` を使用している場合、 `ルールセット` 毎にレギュレーション設定が行われる。

| 個別セクション名は `regulations-section` / `regulations_team-section` の前後のどちらかに *ルール識別子* が付いた形となる。
| 個別レギュレーションは `main-config` 、及び `rule-config` で定義可能。

読み込み優先順位
----------------

| 読み込みには優先順位があり、最初に見つかった設定のみが取り込まれる。
| 個別セクションが無い場合は `regulations-section` / `regulations_team-section` が読み込まれる。

.. note::
   レギュレーション設定が必要ない場合は、空の個別セクションを定義すること。

   `regulations-section` / `regulations_team-section` の定義はすべてルールセットで読み込みが発生するため、デフォルト設定として動作する。


個人清算レギュレーション
++++++++++++++++++++++++

.. list-table::
   :width: 100%
   :widths: 5 20 40
   :header-rows: 1

   * - 優先順位
     - 定義箇所
     - セクション名
   * - 1
     - `rule-config`
     - {rule_version}_regulations
   * - 2
     - `rule-config`
     - regulations_{rule_version}
   * - 3
     - `main-config`
     - {rule_version}_regulations
   * - 4
     - `main-config`
     - regulations_{rule_version}
   * - 5
     - `main-config`
     - regulations


チーム清算レギュレーション
++++++++++++++++++++++++++


.. list-table::
   :width: 100%
   :widths: 5 20 40
   :header-rows: 1

   * - 優先順位
     - 定義箇所
     - セクション名
   * - 1
     - `rule-config`
     - {rule_version}_regulations_team
   * - 2
     - `rule-config`
     - regulations_team_{rule_version}
   * - 3
     - `main-config`
     - {rule_version}_regulations_team
   * - 4
     - `main-config`
     - regulations_team_{rule_version}
   * - 5
     - `main-config`
     - regulations_team
