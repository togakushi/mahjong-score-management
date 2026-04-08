.. _web-section:

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
   * - :index:`host <pair: web section; host>`
     -
     - 文字列
     - 127.0.0.1
     -
   * - :index:`port <pair: web section; port>`
     -
     - 数値
     - 8000
     -
   * - :index:`require_auth <pair: web section; require_auth>`
     - BASIC認証の利用
     - 真偽値
     - False
     - ``username`` / ``password`` のいずれかが未定義なら強制的に ``False`` になる
   * - :index:`username <pair: web section; username>`
     - 認証ユーザ名
     - 文字列
     - 空欄
     -
   * - :index:`password <pair: web section; password>`
     - 認証パスワード
     - 文字列
     - 空欄
     - 平文指定
   * - :index:`use_ssl <pair: web section; use_ssl>`
     - HTTPSの利用
     - 真偽値
     - False
     - ``certificate`` / ``private_key`` のいずれかが未定義なら強制的に ``False`` になる
   * - :index:`certificate <pair: web section; certificate>`
     - サーバー証明書保存パス
     - 文字列
     - 空欄
     -
   * - :index:`private_key <pair: web section; private_key>`
     - 秘密鍵保存パス
     - 文字列
     - 空欄
     -
   * - :index:`view_summary <pair: web section; view_summary>`
     - 成績サマリメニューの表示
     - 真偽値
     - True
     -
   * - :index:`view_graph <pair: web section; view_graph>`
     - グラフメニューの表示
     - 真偽値
     - True
     -
   * - :index:`view_ranking <pair: web section; view_ranking>`
     - ランキングメニューの表示
     - 真偽値
     - True
     -
   * - :index:`management_member <pair: web section; management_member>`
     - メンバー/チーム編集メニューの表示
     - 真偽値
     - False
     -
   * - :index:`management_score <pair: web section; management_score>`
     - 成績管理メニューの表示
     - 真偽値
     - False
     -
   * - :index:`theme <pair: web section; theme>`
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
   * - :index:`custom_css <pair: web section; custom_css>`
     - カスタマイズスタイルシート [#]_
     - 文字列(ファイルパス)
     - 空欄
     - ファイルが存在しない場合は空欄になる
   * - :index:`plotting_backend <pair: web section; plotting_backend>`
     - 文字列
     - 真偽値
     - plotly
     - 共通設定を上書き

.. rubric:: 脚注

.. [#] 設定ファイルからの相対パスで指定
