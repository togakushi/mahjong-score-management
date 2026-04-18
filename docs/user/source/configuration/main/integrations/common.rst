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
   * - .. _channel_config:

       :index:`channel_config <pair: integrations section; channel_config>`
     - `channel-addition` を指定する
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
   * - .. _channel_id:

       :index:`channel_id <pair: integrations section; channel_id>`
     - *チャンネル識別子* を上書きする
     - 文字列
     - None
     - チャンネル個別設定のセクション名は変わらない [#]_
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

..

.. danger:: ``plotting_backend`` は実装状況によってはデフォルト値から変更するとアプリケーションエラーとなり、正しく動作しなくなる。

.. rubric:: 脚注

.. [#] `channel_id <channel_id>` で使用するチャンネル識別子を変更している状態でもチャンネル個別設定のセクション名は ``<サービス名>_<チャンネルID>`` となる。


データベースファイル切替
------------------------

`channel_config <channel_config>` でメイン設定の `database_file <database_file>` が再定義できるため、別のDBファイルに情報を蓄積することが可能となる。

.. warning::
   以下の機能はDB切替実装が完了していないため、メイン設定にある `database_file <database_file>` が利用される。

   - homeタブからの操作
   - `dbtools.py` によるDBメンテナンス

channel_id / separate について
------------------------------

| `channel_id <channel_id>` / ``separate`` は複数箇所で定義できる。
| 以下の順序で探索し、最初に未定義時の状態から変更されたものが設定値として採用される。

.. list-table::
   :width: 100%
   :widths: 5 15 30 30
   :header-rows: 1

   * - 探索順序
     - 設定ファイル
     - 記述セクション
     - 設定が有効になる範囲
   * - 1
     - `channel-addition`
     - `channel-addition` 内の `setting-section`
     - 指定チャンネルの範囲
   * - 2
     - `main-config`
     - チャンネル個別設定

       - slack `slack-channel-settings`
       - discord `discord-channel-settings`
     - 指定チャンネルの範囲
   * - 3
     - `main-config`
     - `integrations-common`
     - 連携サービスの範囲
   * - 4
     - `main-config`
     - `setting-section`
     - アプリケーション全体(すべてのサービス、すべてのチャンネル)
