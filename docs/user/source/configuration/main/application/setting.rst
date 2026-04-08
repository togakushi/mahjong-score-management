.. _setting-section:

settingセクション
=================

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - :index:`rule_config web section<pair: setting section; rule_config>`
     - ルールセット定義ファイルパスを指定
     - | 文字列
       | (ファイルパス)
     - None
     - mahjongセクションの定義もない場合、 ``files/default_rule.ini`` が使用される
   * - :index:`default_rule web section<pair: setting section; default_rule>`
     - ルール識別子未指定に使用するデフォルト値
     - 文字列
     - 最初に定義されたルールセットのルール識別子
     -
   * - :index:`separate web section<pair: setting section; separate>`
     - スコア入力元(チャンネル識別子)単位の集計
     - 真偽値
     - False
     - *True* : 集計条件にチャンネル識別子を追加
   * - :index:`channel_id web section<pair: setting section; channel_id>`
     - チャンネル識別子を上書きする
     - 文字列
     - None
     -
   * - :index:`remarks_suffix web section<pair: setting section; remarks_suffix>`
     - *成績登録ワード* と `remarks_suffix` の組み合わせをメモ登録ワードとする
     - | 文字列
       | (カンマ区切り)
     - ``remarks`` の定義がない場合のみ
     - カンマ区切りで複数ワードの設定が可能
   * - :index:`guest_mark web section<pair: setting section; guest_mark>`
     - ゲストに付ける記号
     - 文字列
     - ※
     -
   * - :index:`search_word web section<pair: setting section; search_word>`
     - キーワード「コメント」に指定文字列を常につける
     - 文字列
     -
     - コメント検索しか行わなくなる(専用化)
   * - :index:`group_length web section<pair: setting section; group_length>`
     - 集約キーワードを指定しなかった場合に集約する文字数
     - 数値(int)
     - 未定義時
     - :option:`共通(コメント検索) 集約\<NNN>` で上書きされる
   * - :index:`time_adjust web section<pair: setting section; time_adjust>`
     - 日付変更後、指定時間までを1日単位の集計に含める
     - 数値(int)
     - 12
     - 1時間単位で指定
   * - :index:`font_file web section<pair: setting section; font_file>`
     - グラフ描写に使用する日本語フォントファイル [1]_
     - 文字列
     - ``ipaexg.ttf``
     -
   * - :index:`graph_style web section<pair: setting section; graph_style>`
     - グラフに使用するスタイル
     - 文字列
     - ``ggplot``
     - `Style sheets`_ から選択
   * - :index:`work_dir web section<pair: setting section; work_dir>`
     - 生成ファイルの保存先 [1]_
     - 文字列<br>(ディレクトリ名)
     - ``work``
     - 画像ファイル、PDFファイルの保存先
   * - :index:`database_file web section<pair: setting section; database_file>`
     - 成績を記録するファイル名 [2]_
     - | 文字列
       | (ファイルパス)
     - ``mahjong.db``
     - SQLite 3.x database
   * - :index:`backup_dir web section<pair: setting section; backup_dir>`
     - 自動バックアップ保存先 [2]_
     - | 文字列
       | (ディレクトリ名)
     - None
     - 空欄(None)時はバックアップしない

.. tip::
   :manpage:`default_rule.ini` には **default_rule** (四人打ち用ルールセット)と **default_rule3** (三人打ち用ルールセット)が定義されている。

.. rubric:: 脚注

.. [1] 設定ファイルからの相対パスで指定、見つからなければスクリプトからの相対パス
.. [2] 設定ファイルからの相対パスで指定

.. _Style sheets: https://matplotlib.org/stable/gallery/style_sheets/index.html
