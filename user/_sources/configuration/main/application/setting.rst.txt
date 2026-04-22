.. index::
   pair: メイン設定; setting section
   :name: setting-section

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
   * - .. setting_section:: rule_config
     - `rule-config` のパスを指定
     - | 文字列
       | (ファイルパス)
     - None
     - `mahjong-section` に有効な `ルールセット` 定義もない場合、 :manpage:`default_rule.ini` が使用される
   * - .. setting_section:: default_rule
     - *ルール識別子* 未指定に使用するデフォルト値
     - 文字列
     - 最初に定義された `ルールセット` の *ルール識別子*
     -
   * - .. setting_section:: separate
     - スコア入力元(チ *ャンネル識別子* )単位の集計
     - 真偽値
     - False
     - :True: 集計条件に *チャンネル識別子* を追加
   * - .. setting_section:: channel_id
     - *チャンネル識別子* を上書きする
     - 文字列
     - None
     -
   * - .. setting_section:: remarks_suffix
     - *成績記録キーワード* と `remarks_suffix` の組み合わせを *メモ記録ワード* とする
     - | 文字列
       | (カンマ区切り)
     - 空欄
     - `rule-set` で `remarks` の定義がない場合のみに使用される
   * - .. setting_section:: guest_mark
     - ゲストに付ける記号
     - 文字列
     - ※
     -
   * - .. setting_section:: search_word
     - キーワード「コメント」に指定文字列を常につける
     - 文字列
     -
     - コメント検索しか行わなくなる(専用化)
   * - .. setting_section:: group_length
     - 集約キーワードを指定しなかった場合に集約する文字数
     - 数値(int)
     - 未定義時
     - :common:`集約\<NNN>` で上書きされる
   * - .. setting_section:: time_adjust
     - 日付変更後、指定時間までを1日単位の集計に含める
     - 数値(int)
     - 12
     - 1時間単位で指定
   * - .. setting_section:: font_file
     - グラフ描写に使用する日本語フォントファイル [1]_
     - 文字列
     - ``ipaexg.ttf``
     -
   * - .. setting_section:: graph_style
     - グラフに使用するスタイル
     - 文字列
     - ``ggplot``
     - `Style sheets`_ から選択
   * - .. setting_section:: work_dir
     - 生成ファイルの保存先 [1]_
     - | 文字列
       | (ディレクトリ名)
     - ``work``
     - 画像ファイル、PDFファイルの保存先
   * - .. setting_section:: database_file
     - 成績を記録するファイル名 [2]_
     - | 文字列
       | (ファイルパス)
     - ``mahjong.db``
     - SQLite 3.x database
   * - .. setting_section:: backup_dir
     - 自動バックアップ保存先 [2]_
     - | 文字列
       | (ディレクトリ名)
     - None
     - 空欄(None)時はバックアップしない

..

.. tip::
   :manpage:`default_rule.ini` には **default_rule** (四人打ち用ルールセット)と **default_rule3** (三人打ち用ルールセット)が定義されている。

----

.. rubric:: 脚注
   :heading-level: 6

.. [1] 設定ファイルからの相対パスで指定、見つからなければスクリプトからの相対パス
.. [2] 設定ファイルからの相対パスで指定

.. _Style sheets: https://matplotlib.org/stable/gallery/style_sheets/index.html
