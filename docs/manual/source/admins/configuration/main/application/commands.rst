.. index::
   single: メイン設定; 成績管理
   pair: メイン設定; summary section
   pair: メイン設定; analysis section
   pair: メイン設定; help section
   :name: results_management

成績管理
========

| ``summary`` / ``analysis`` / ``help`` の各セクションで定義できる項目。
| すべてのセクションでパラメータの定義は可能だが、動作に影響があるのもは以下の表のとおりとなる。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 10 10 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - summary
     - analysis
     - help
     - 備考
   * - .. sub_commands_section:: commandword
     - 機能を呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     - `function-call-keyword` 参照
     - |:/:|
     - |:/:|
     - |:/:|
     - カンマ区切りで複数ワードの設定が可能
   * - .. sub_commands_section:: command_suffix
     - `成績記録キーワード <keywords>` と :sub_commands_section:`command_suffix` の組み合わせを機能呼び出しキーワードとする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - |:/:|
     - |:/:|
     - |:/:|
     - カンマ区切りで複数ワードの設定が可能
   * - .. sub_commands_section:: aggregation_range
     - 検索範囲未指定時のデフォルト値
     - 文字列
     - 当日
     - |:/:|
     - |:/:|
     -
     -
   * - .. sub_commands_section:: dropitems
     - 非表示にする項目を指定
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - |:/:|
     - |:/:|
     - |:/:|
     - `rule-set` の :rule_set_section:`dropitems` も追加される

       .. seealso:: `function-dropitems`

   * - .. sub_commands_section:: unregistered_replace
     - 未登録プレイヤーを `guest_name` に置き換えて表示
     - 真偽値
     - True
     - |:/:|
     - |:/:|
     -
     -
   * - .. sub_commands_section:: guest_skip
     - 未登録プレイヤーの結果を無視する
     - 真偽値
     - True
     - |:/:|
     - |:/:|
     -
     - 全体成績用
   * - .. sub_commands_section:: guest_skip2
     - 未登録プレイヤーの結果を無視する
     - 真偽値
     - True
     - |:/:|
     - |:/:|
     -
     - 個人成績用
   * - .. sub_commands_section:: comparisons
     - 比較モードで表示する
     - 真偽値
     - False
     -
     -
     -
     - 内部フラグ（ ``True`` 指定時は強制的に比較モードになる）
   * - .. sub_commands_section:: game_results
     - 戦績(ゲーム単位の素点と順位)を表示
     - 真偽値
     - False
     -
     -
     -
     - 内部フラグ（ ``True`` 指定時は強制表示 ）
   * - .. sub_commands_section:: versus
     - 対戦マトリクス表示
     - 真偽値
     - False
     -
     -
     -
     - 内部フラグ（ ``True`` 指定時は強制表示 ）
   * - .. sub_commands_section:: individual
     - デフォルトの集計対象を切り替え
     - 真偽値
     - True
     - |:/:|
     - |:/:|
     -
     - :True: 個人成績
       :False: チーム成績
   * - .. sub_commands_section:: statistics
     - 「統計」オプションを常に指定
     - 真偽値
     - False
     - |:/:|
     - |:/:|
     -
     - :True: 統計情報の強制表示
       :False: 統計オプションの指定状態に依存
   * - .. sub_commands_section:: always_argument
     - コマンドに常に指定する文字列を追加
     - 文字列
     - 空欄
     - |:/:|
     - |:/:|
     -
     - キーで指定しているデフォルト値は上書きされる
   * - .. sub_commands_section:: stipulated
     - 規定打数(指定値固定)
     - 数値(int)
     - 1
     - |:/:|
     - |:/:|
     -
     - ``0`` が指定されている場合は `stipulated_rate` を使う
   * - .. sub_commands_section:: stipulated_rate
     - 規定打数を対戦数よって決める
     - 数値(float)
     - 0.05
     - |:/:|
     - |:/:|
     -
     - 対戦数 × `stipulated_rate` （切り上げ）+ 1
   * - .. sub_commands_section:: ranked
     - 出力される順位制限
     - 数値(int)
     - 3
     -
     - |:/:|
     -
     - `deliverables-ranking` / `deliverables-rating_table` で使用する
   * - .. sub_commands_section:: interval
     - 集計範囲の区切り指定
     - 数値(int)
     - 80
     -
     - |:/:|
     -
     - `deliverables-results_analysis` で使用する
..


.. _function-call-keyword:

コマンド呼び出しキーワード
--------------------------

各種コマンドを呼び出すキーワードはディスパッチテーブルに登録され、登録済みのキーワードと一致したときにそのコマンドが呼び出される。

| :sub_commands_section:`commandword` 、 :sub_commands_section:`command_suffix` の定義状況によって登録される呼び出しキーワードが変化する。
| :sub_commands_section:`commandword` の定義が優先的に登録され、 :sub_commands_section:`command_suffix` の定義があれば、 `rule-set` の `keywords` と :sub_commands_section:`command_suffix` の組み合わせが登録される。

.. flat-table::
   :width: 100%
   :widths: 10 10 10 30
   :header-rows: 1

   * - commandword
     - | keywords
       | (成績記録キーワード)
     - command_suffix
     - 登録されるキーワード
   * - |:x:|
     - |:x:|
     - |:x:|
     - :rspan:`2` デフォルトキーワード

       :summary: 成績集計
       :analysis: 成績分析
       :help: 麻雀ヘルプ
       :member: メンバー一覧
       :team: チーム一覧
   * - |:x:|
     - |:x:|
     - |:o:|
   * - |:x:|
     - |:o:|
     - |:x:|
   * - |:x:|
     - |:o:|
     - |:o:|
     - `keywords` + :sub_commands_section:`command_suffix` の組み合わせ
   * - |:o:|
     - |:x:|
     - |:x:|
     - :rspan:`3` :sub_commands_section:`commandword` で定義したワード
   * - |:o:|
     - |:x:|
     - |:o:|
   * - |:o:|
     - |:o:|
     - |:x:|
   * - |:o:|
     - |:o:|
     - |:o:|



パラメータの評価順序
--------------------

以下の順に評価され、値を上書きしていく。

#. メイン設定ファイルからデフォルト値読み込み

   - チャンネル個別設定ファイルがあれは上書き

#. `always_argument` の処理
#. コマンドから与えられた引数の処理

コマンドからの `date-specification` があれば指定されている範囲だけが対象になる。

.. tip::
   - `always_argument` で ``今年`` と定義した状態でコマンドから ``今月 先月`` と指定した場合の範囲は ``今月 先月`` となる
   - コマンドからの日付指定がない場合は ``今年`` だけが範囲になる
   - コマンドからの指定があれば設定ファイルの値は無視される
