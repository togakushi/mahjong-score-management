.. _function-members_list:

メンバー一覧表示
================

`レギュラーメンバー` の一覧を表示する。

:コマンドタイプ: `function-others`
:必須オプション: なし
:ターゲット指定: 無効
:個別オプション: `あり <option-others>`


コマンド構文
------------

:チャンネル内呼び出し: <メンバー一覧表示コマンド> [:common:`詳細`]

   .. note:: ``メンバー一覧表示コマンド`` は以下で定義される

      - `member-section` の :member_section:`commandword`

:スラッシュコマンド: /commandname member

   .. seealso:: `slash_commands-member` コマンド

   .. include:: /material/commandname.inc

オプション
----------

.. flat-table::
   :header-rows: 1
   :width: 100%
   :widths: 10 20 70

   * - 分類
     - 項目
     - 内容
   * - 個別オプション
     - :common:`詳細`
     - 各メンバーの最終更新日、経過日数、総対戦数を表示する
   * - 共通オプション
     - `rule-search`
     - `ルール識別子` を指定する
..


項目説明
--------

通常表示
   :表示名: 成績管理などで表示される名前
   :登録されている名前: 別名登録されている名前のリスト

詳細表示
   :メンバー名: 登録されている `レギュラーメンバー` の名前
   :最終更新日: 最後に記録された `score-record` の日時
   :経過日数: 最終更新日から `function-members_list` コマンド実行日時の差
   :総対戦数: 記録されている結果の総数

   .. caution::

      最終更新日、総対戦数は指定されている `ルール識別子` を対象にカウントされる
