.. _integrations-common:

共通設定
========

各サービスのセクションで設定できる共通設定。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - :index:`channel_config <pair: integrations section; channel_config>`
     - チャンネル個別設定ファイル
     - 文字列(ファイルパス)
     - None
     - `main-config` とマージ
   * - :index:`badge_degree <pair: integrations section; badge_degree>`
     - ゲーム数に応じて表示される称号
     - 真偽値
     - False
     - `degree-section`
   * - :index:`badge_status <pair: integrations section; badge_status>`
     - 勝利によって表示される調子バッヂ
     - 真偽値
     - False
     - `status-section`
   * - :index:`badge_grade <pair: integrations section; badge_grade>`
     - 段位表示
     - 真偽値
     - False
     - `grade-section`
   * - :index:`channel_id <pair: integrations section; channel_id>`
     - *チャンネル識別子* を上書きする
     - 文字列
     - None
     - チャンネル個別設定のセクション名変わらない [^1]
   * - :index:`separate <pair: integrations section; separate>`
     - スコア入力元( *チャンネル識別子* )単位の集計
     - 真偽値
     - False
     - :True: 集計条件に *チャンネル識別子* を追加
   * - :index:`plotting_backend <pair: integrations section; plotting_backend>`
     - グラフ生成ライブラリ選択
     - 文字列
     - matplotlib
     - ``matplotlib`` / ``plotly`` から選択

.. danger:: ``plotting_backend`` は実装状況によってはデフォルト値から変更するとエラーとなる。

channel_config について
-----------------------

| ``channel_config`` で指定した設定ファイルの ``setting``、 ``results``、 ``graph``、 ``ranking``、 ``report``、 ``custom_message`` のセクションをメイン設定のパラメータとマージする。
| `custom_message-section` 以外の各セクションで設定された値は以下の順でマージされるため、未定義の設定はメイン設定の値を引き継ぐ。

#. メイン設定セクション読み込み
#. チャンネル個別設定セクション読み込み

`custom_message-section` が定義されていればメイン設定の内容を上書き、未定義時はメイン設定の値が引き継がれる。

.. important:: メイン設定の `commandword <commandword>` で指定されているキーワードは上書きできない。

[^1]: ``channel_id`` で使用するチャンネル識別子を変更している状態でもチャンネル個別設定のセクション名は ``<サービス名>_<チャンネルID>`` となる。

データベースファイル切替
------------------------

``channel_config`` でメイン設定の`database_file`が再定義できるため、別のDBファイルに情報を蓄積することが可能となる。

.. warning::
   以下の機能はDB切替実装が完了していないため、メイン設定にある ``database_file`` が利用される。

   - homeタブからの操作
   - `dbtools.py` によるDBメンテナンス

channel_id / separate について
------------------------------

| ``channel_id`` / ``separate`` は複数箇所で定義できる。
| 以下の順序で探索し、最初に未定義時の状態から変更されたものが設定値として採用される。

.. list-table::
   :width: 100%
   :widths: 5 15 30 30
   :header-rows: 1

   * - 優先度
     - 設定ファイル
     - 記述セクション
     - 設定が有効になる範囲
   * - 1
     - チャンネル個別設定
     - チャンネル個別設定ファイル内settingセクション
     - 指定チャンネルの範囲
   * - 2
     - メイン設定
     - チャンネル個別設定

       - slack `slack-channel-settings`
       - discord `discord-channel-settings`
     - 指定チャンネルの範囲
   * - 3
     - メイン設定
     - `integrations-common`
     - 連携サービスの範囲
   * - 4
     - メイン設定
     - `setting-section`
     - アプリケーション全体(すべてのサービス、すべてのチャンネル)
