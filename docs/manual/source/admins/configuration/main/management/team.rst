.. index::
   pair: メイン設定; team section
   :name: team-section

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
   * - .. team_section:: commandword
     - `function-team_list` を呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     - チーム一覧
     - カンマ区切りで複数ワードの設定が可能
   * - .. team_section:: command_suffix
     - `成績記録キーワード <keywords>` と :team_section:`command_suffix` の組み合わせを `function-team_list` の呼び出しキーワードにする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - .. seealso:: `function-call-keyword`
   * - .. team_section:: registration_limit
     - 登録チーム数上限
     - 数値(int)
     - 255
     -
   * - .. team_section:: character_limit
     - 登録チーム名文字数上限
     - 数値(int)
     - 16
     -
   * - .. team_section:: member_limit
     - チーム構成メンバー上限
     - 数値(int)
     - 16
     -
   * - .. team_section:: friendly_fire
     - 同じチームが同卓しているゲームを集計対象にする
     - 真偽値
     - True
     -
