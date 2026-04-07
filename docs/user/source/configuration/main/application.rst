.. index::
   single: メイン設定; アプリケーション設定

アプリケーション設定
====================

.. _setting-section:

settingセクション
-----------------

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - :index:`rule_config <single: setting; rule_config>`
     - ルールセット定義ファイルパスを指定
     - | 文字列
       | (ファイルパス)
     - None
     - mahjongセクションの定義もない場合、 ``files/default_rule.ini`` が使用される
   * - :index:`default_rule <single: setting; default_rule>`
     - ルール識別子未指定に使用するデフォルト値
     - 文字列
     - 最初に定義されたルールセットのルール識別子
     -
   * - :index:`separate <single: setting; separate>`
     - スコア入力元(チャンネル識別子)単位の集計
     - 真偽値
     - False
     - *True* : 集計条件にチャンネル識別子を追加
   * - :index:`channel_id <single: setting; channel_id>`
     - チャンネル識別子を上書きする
     - 文字列
     - None
     -
   * - :index:`remarks_suffix <single: setting; remarks_suffix>`
     - *成績登録ワード* と `remarks_suffix` の組み合わせをメモ登録ワードとする
     - | 文字列
       | (カンマ区切り)
     - ``remarks`` の定義がない場合のみ
     - カンマ区切りで複数ワードの設定が可能
   * - :index:`guest_mark <single: setting; guest_mark>`
     - ゲストに付ける記号
     - 文字列
     - ※
     -
   * - :index:`search_word <single: setting; search_word>`
     - キーワード「コメント」に指定文字列を常につける
     - 文字列
     -
     - コメント検索しか行わなくなる(専用化)
   * - :index:`group_length <single: setting; group_length>`
     - 集約キーワードを指定しなかった場合に集約する文字数
     - 数値(int)
     - 未定義時
     - 集約オプション( :option:`コメント\<XXX>` )で上書き指定可
   * - :index:`time_adjust <single: setting; time_adjust>`
     - 日付変更後、指定時間までを1日単位の集計に含める
     - 数値(int)
     - 12
     - 1時間単位で指定
   * - :index:`font_file <single: setting; font_file>`
     - グラフ描写に使用する日本語フォントファイル [1]_
     - 文字列
     - ``ipaexg.ttf``
     -
   * - :index:`graph_style <single: setting; graph_style>`
     - グラフに使用するスタイル
     - 文字列
     - ``ggplot``
     - `Style sheets`_ から選択
   * - :index:`work_dir <single: setting; work_dir>`
     - 生成ファイルの保存先 [1]_
     - 文字列<br>(ディレクトリ名)
     - ``work``
     - 画像ファイル、PDFファイルの保存先
   * - :index:`database_file <single: setting; database_file>`
     - 成績を記録するファイル名 [2]_
     - | 文字列
       | (ファイルパス)
     - ``mahjong.db``
     - SQLite 3.x database
   * - :index:`backup_dir <single: setting; backup_dir>`
     - 自動バックアップ保存先 [2]_
     - | 文字列
       | (ディレクトリ名)
     - None
     - 空欄(None)時はバックアップしない

.. tip::
   [*default_rule.ini*](../../files/default_rule.ini)には ***default_rule*** (四人打ち用ルールセット)と ***default_rule3*** (三人打ち用ルールセット)が定義されている。\

.. rubric:: 脚注

.. [1] 設定ファイルからの相対パスで指定、見つからなければスクリプトからの相対パス
.. [2] 設定ファイルからの相対パスで指定

.. _Style sheets: https://matplotlib.org/stable/gallery/style_sheets/index.html

----


aliasセクション
---------------

スラッシュコマンド使用時のサブコマンドの別名を定義。

カンマ区切りで複数ワードの設定が可能。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - results
     - 成績表示
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - graph
     - グラフ表示
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - ranking
     - ランキング表示
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - report
     - レポート表示
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - download
     - データベースダウンロード
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - member
     - メンバーリスト表示
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - add
     - メンバー追加
     - | 文字列
       | (カンマ区切り)
     -
     - メンバー新規登録、別名登録
   * - del
     - メンバー削除
     - | 文字列
       | (カンマ区切り)
     -
     - メンバー削除、別名削除
   * - team_create
     - 新規チーム作成
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - team_del
     - チーム削除
     - | 文字列
       | (カンマ区切り)
     -
     - チームに所属していたメンバーは未所属になる
   * - team_add
     - チームにメンバーを所属
     - | 文字列
       | (カンマ区切り)
     -
     - - 複数チームに所属できない
       - 未登録メンバー(ゲスト)はチーム所属できない
   * - team_remove
     - チームからメンバーを削除
     - | 文字列
       | (カンマ区切り)
     -
     - チーム所属から外れたメンバーは未所属になる
   * - team_list
     - チーム一覧と所属メンバーの表示
     - | 文字列
       | (カンマ区切り)
     -
     -
   * - team_clear
     - すべてのチーム情報を削除
     - | 文字列
       | (カンマ区切り)
     -
     - すべてのチーム情報を削除し、全員未所属にする
