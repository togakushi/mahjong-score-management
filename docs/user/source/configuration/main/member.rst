.. index::
   single: メイン設定; メンバー管理

メンバー管理
============

登録メンバー数の上限、文字数制限などを設ける。

memberセクション
----------------

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - :index:`commandword <single: member; commandword>`
     - メンバー一覧を表示するコマンドの呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     - メンバー一覧
     - カンマ区切りで複数ワードの設定が可能
   * - :index:`command_suffix <single: member; command_suffix>`
     - *成績登録ワード* と ``command_suffix`` の組み合わせを機能を呼び出すキーワードとする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     -
   * - :index:`registration_limit <single: member; registration_limit>`
     - 登録メンバー数上限
     - 数値(int)
     - 255
     -
   * - :index:`character_limit <single: member; character_limit>`
     - 登録メンバー名文字数上限
     - 数値(int)
     - 8
     -
   * - :index:`alias_limit <single: member; alias_limit>`
     - 別名登録上限数
     - 数値(int)
     - 16
     -
   * - :index:`guest_name <single: member; guest_name>`
     - 未登録メンバーを置換するときの名前
     - 文字列
     - ゲスト
     -

teamセクション
--------------

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - :index:`commandword <single: team; commandword>`
     - チーム一覧を表示するコマンドを呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     - チーム一覧
     - カンマ区切りで複数ワードの設定が可能
   * - :index:`command_suffix <single: team; command_suffix>`
     - *成績登録ワード* と ``command_suffix`` の組み合わせを機能を呼び出すキーワードとする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     -
   * - :index:`registration_limit <single: team; registration_limit>`
     - 登録チーム数上限
     - 数値(int)
     - 255
     -
   * - :index:`character_limit <single: team; character_limit>`
     - 登録チーム名文字数上限
     - 数値(int)
     - 16
     -
   * - :index:`member_limit <single: team; member_limit>`
     - チーム構成メンバー上限
     - 数値(int)
     - 16
     -
   * - :index:`friendly_fire <single: team; friendly_fire>`
     - 同じチームが同卓しているゲームを集計対象にする
     - 真偽値
     - True
     -
