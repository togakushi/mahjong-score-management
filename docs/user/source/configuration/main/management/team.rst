.. _team-section:

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
   * - :index:`commandword <pair: team section; commandword>`
     - チーム一覧を表示するコマンドを呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     - チーム一覧
     - カンマ区切りで複数ワードの設定が可能
   * - :index:`command_suffix <pair: team section; command_suffix>`
     - *成績登録ワード* と ``command_suffix`` の組み合わせを機能を呼び出すキーワードとする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     -
   * - :index:`registration_limit <pair: team section; registration_limit>`
     - 登録チーム数上限
     - 数値(int)
     - 255
     -
   * - :index:`character_limit <pair: team section; character_limit>`
     - 登録チーム名文字数上限
     - 数値(int)
     - 16
     -
   * - :index:`member_limit <pair: team section; member_limit>`
     - チーム構成メンバー上限
     - 数値(int)
     - 16
     -
   * - :index:`friendly_fire <pair: team section; friendly_fire>`
     - 同じチームが同卓しているゲームを集計対象にする
     - 真偽値
     - True
     -
