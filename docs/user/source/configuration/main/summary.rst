.. index::
   single: メイン設定; 成績管理
   pair: メイン設定; results section
   pair: メイン設定; graph section
   pair: メイン設定; ranking section
   pair: メイン設定; report section
   pair: メイン設定; help section

成績管理
========

| ``results`` ``graph`` ``ranking`` ``report`` ``help`` の各セクションで定義できる項目。
| すべてのセクションでパラメータの定義は可能だが、動作に影響があるのもは以下の表のとおりとなる。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 10 10 10 10 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - results
     - graph
     - ranking
     - report
     - help
     - 備考
   * - _`commandword`
     - 機能を呼び出すキーワード
     - | 文字列
       | (カンマ区切り)
     -
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     - カンマ区切りで複数ワードの設定が可能
   * - _`command_suffix`
     - *成績記録キーワード* と `command_suffix <command_suffix>` の組み合わせを機能を呼び出すキーワードとする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     - カンマ区切りで複数ワードの設定が可能
   * - aggregation_range
     - 検索範囲未指定時のデフォルト値
     - 文字列
     - 当日
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     -
     -
   * - unregistered_replace
     - 未登録プレイヤーを `guest_name <guest_name>` に置き換えて表示
     - 真偽値
     - True
     - |:/:|
     - |:/:|
     - |:/:|
     -
     -
     -
   * - guest_skip
     - 未登録プレイヤーの結果を無視する
     - 真偽値
     - True
     - |:/:|
     - |:/:|
     - |:/:|
     -
     -
     - 全体成績用
   * - guest_skip2
     - 未登録プレイヤーの結果を無視する
     - 真偽値
     - True
     - |:/:|
     - |:/:|
     - |:/:|
     -
     -
     - 個人成績用
   * - score_comparisons
     - 比較モードで表示する
     - 真偽値
     - False
     -
     -
     -
     -
     -
     - 内部フラグ（ ``True`` 指定時は強制的に比較モードになる）
   * - game_results
     - 戦績(ゲーム単位の素点と順位)を表示
     - 真偽値
     - False
     -
     -
     -
     -
     -
     - 内部フラグ（ ``True`` 指定時は強制的表示 ）
   * - versus_matrix
     - 対戦マトリックス表示
     - 真偽値
     - False
     -
     -
     -
     -
     -
     - 内部フラグ（ ``True`` 指定時は強制的表示 ）
   * - individual
     - デフォルトの集計対象を切り替え
     - 真偽値
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     - :True: 個人成績
       :False: チーム成績
   * - statistics
     - 「統計」オプションを常に指定
     - 型
     - |:/:|
     -
     -
     -
     -
     -
     - 座席データ、レコードを常に表示する
   * - always_argument
     - コマンドに常に指定する文字列を追加
     - 文字列
     - 空欄
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     -
     - キーで指定しているデフォルト値は上書きされる
   * - stipulated
     - 規定打数(指定値固定)
     - 数値(int)
     - 1
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     -
     - ``0`` が指定されている場合は ``stipulated_rate`` を使う
   * - stipulated_rate
     - 規定打数を集計ゲーム数よって決める
     - 数値(float)
     - 0.05
     - |:/:|
     - |:/:|
     - |:/:|
     - |:/:|
     -
     - 集計ゲーム数 × ``stipulated_rate`` （切り上げ）+ 1

..

.. _function-call-keyword:

機能呼び出しキーワード
----------------------

各種機能を呼び出すキーワードはディスパッチテーブルに登録され、登録済みのキーワードと一致したときにその機能が呼び出される。

| `commandword <commandword>` 、 `command_suffix <command_suffix>` の定義状況によって登録される呼び出しキーワードが変化する。
| `commandword <commandword>` の定義が優先的に登録される。
| `command_suffix <command_suffix>` の定義があれば、 `rule-set` の `keywords <keywords>` と `command_suffix <command_suffix>` の組み合わせが登録される。

.. list-table::
   :width: 100%
   :widths: 10 10 10 30
   :header-rows: 1

   * - commandword
     - command_suffix
     - | keywords
       | (成績記録キーワード)
     - 登録されるキーワード
   * - |:x:|
     - |:x:|
     - |:x:|
     - デフォルトキーワード
   * - |:o:|
     - |:x:|
     - |:x:|
     - `commandword <commandword>`
   * - |:o:|
     - |:x:|
     - |:o:|
     - `commandword <commandword>`
   * - |:o:|
     - |:o:|
     - |:x:|
     - `commandword <commandword>`
   * - |:o:|
     - |:o:|
     - |:o:|
     - `commandword <commandword>`
   * - |:x:|
     - |:x:|
     - |:o:|
     - デフォルトキーワード
   * - |:x:|
     - |:o:|
     - |:x:|
     - デフォルトキーワード
   * - |:x:|
     - |:o:|
     - |:o:|
     - `keywords <keywords>` + `command_suffix <command_suffix>`


パラメータの評価順序
--------------------

以下の順に評価され、値を上書きしていく。

#. メイン設定ファイルからデフォルト値読み込み

   - チャンネル個別設定ファイルがあれは上書き

#. ``always_argument`` の処理
#. コマンドから与えられた引数の処理

コマンドからの `date-specification` があれば指定されている範囲だけが対象になる。

.. tip::
   - ``always_argument`` で ``今年`` と定義した状態でコマンドから ``今月 先月`` と指定した場合の範囲は ``今月 先月`` となる
   - コマンドからの日付指定がない場合は ``今年`` だけが範囲になる
   - コマンドからの指定があれば設定ファイルの値は無視される
