.. index::
   pair: メイン設定; member section
   :name: member-section

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
   * - .. member_section:: commandword
     - `function-members_list` を呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     - メンバー一覧
     - カンマ区切りで複数ワードの設定が可能
   * - .. member_section:: command_suffix
     - `成績記録キーワード <keywords>` と :member_section:`command_suffix` の組み合わせを `function-members_list` の呼び出しキーワードにする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - .. seealso:: `function-call-keyword`
   * - .. member_section:: registration_limit
     - 登録メンバー数上限
     - 数値(int)
     - 255
     -
   * - .. member_section:: character_limit
     - 登録メンバー名文字数上限
     - 数値(int)
     - 8
     -
   * - .. member_section:: alias_limit
     - 別名登録上限数
     - 数値(int)
     - 16
     -
   * - .. member_section:: guest_name
     - 未登録メンバーを置換するときの名前
     - 文字列
     - ゲスト
     -
