.. _member-section:

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
   * - :index:`commandword <pair: member section; commandword>`
     - メンバー一覧を表示するコマンドの呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     - メンバー一覧
     - カンマ区切りで複数ワードの設定が可能
   * - :index:`command_suffix <pair: member section; command_suffix>`
     - *成績登録ワード* と ``command_suffix`` の組み合わせを機能を呼び出すキーワードとする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     -
   * - :index:`registration_limit <pair: member section; registration_limit>`
     - 登録メンバー数上限
     - 数値(int)
     - 255
     -
   * - :index:`character_limit <pair: member section; character_limit>`
     - 登録メンバー名文字数上限
     - 数値(int)
     - 8
     -
   * - :index:`alias_limit <pair: member section; alias_limit>`
     - 別名登録上限数
     - 数値(int)
     - 16
     -
   * - :index:`guest_name <pair: member section; guest_name>`
     - 未登録メンバーを置換するときの名前
     - 文字列
     - ゲスト
     -
