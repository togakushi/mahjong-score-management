.. index::
   pair: メイン設定; web section
   :name: web-section

webセクション
-------------

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - .. integrations_section:: host
          :category: web section

     -
     - 文字列
     - 127.0.0.1
     -
   * - .. integrations_section:: port
          :category: web section

     -
     - 数値
     - 8000
     -
   * - .. integrations_section:: require_auth
          :category: web section

     - BASIC認証の利用
     - 真偽値
     - False
     - ``username`` / ``password`` のいずれかが未定義なら強制的に ``False`` になる
   * - .. integrations_section:: username
          :category: web section

     - 認証ユーザ名
     - 文字列
     - 空欄
     -
   * - .. integrations_section:: password
          :category: web section

     - 認証パスワード
     - 文字列
     - 空欄
     - 平文指定
   * - .. integrations_section:: use_ssl
          :category: web section

     - HTTPSの利用
     - 真偽値
     - False
     - ``certificate`` / ``private_key`` のいずれかが未定義なら強制的に ``False`` になる
   * - .. integrations_section:: certificate
          :category: web section

     - サーバー証明書保存パス
     - 文字列
     - 空欄
     -
   * - .. integrations_section:: private_key
          :category: web section

     - 秘密鍵保存パス
     - 文字列
     - 空欄
     -
   * - .. integrations_section:: view_summary
          :category: web section

     - 成績サマリメニューの表示
     - 真偽値
     - True
     -
   * - .. integrations_section:: view_graph
          :category: web section

     - グラフメニューの表示
     - 真偽値
     - True
     -
   * - .. integrations_section:: view_ranking
          :category: web section

     - ランキングメニューの表示
     - 真偽値
     - True
     -
   * - .. integrations_section:: management_member
          :category: web section

     - メンバー/チーム編集メニューの表示
     - 真偽値
     - False
     -
   * - .. integrations_section:: management_score
          :category: web section

     - 成績管理メニューの表示
     - 真偽値
     - False
     -
   * - .. integrations_section:: theme
          :category: web section

     - 配色テーマを選択
     - 文字列
     - 空欄
     - | 空欄時はどのスタイルシートも適応されない。
       | 無効なキーワードは無視され、空欄となる。

       :black: 黒色ベースのモノクロ配色
       :midnight: 濃い青色ベースの配色
       :pastel: 明るいパステル調の配色
       :sepia: 明るいセピア調の配色
       :white: 白色ベースのモノクロ配色
   * - .. integrations_section:: custom_css
          :category: web section

     - カスタマイズスタイルシート [#]_
     - 文字列(ファイルパス)
     - 空欄
     - ファイルが存在しない場合は空欄になる
   * - .. integrations_section:: plotting_backend
          :category: web section

     - 文字列
     - 真偽値
     - plotly
     - 共通設定を上書き

..

.. rubric:: 脚注

.. [#] 設定ファイルからの相対パスで指定
