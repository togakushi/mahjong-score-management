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
   * - .. integrations_section:: channel_config
          :category: common

     - `channel-addition` を指定する
     - 文字列(ファイルパス)
     - None
     - `main-config` とマージ
   * - .. integrations_section:: badge_degree
          :category: common

     - ゲーム数に応じて表示される称号
     - 真偽値
     - False
     - `degree-section` で定義した内容を表示する
   * - .. integrations_section:: badge_status
          :category: common

     - 勝利によって表示される調子バッヂ
     - 真偽値
     - False
     - `status-section` で定義した内容を表示する
   * - .. integrations_section:: badge_grade
          :category: common

     - 段位表示
     - 真偽値
     - False
     - | `grade-section` で定義した内容を表示する
       | `draw_split` が ``False`` の場合のみ有効
   * - .. integrations_section:: channel_id
          :category: common

     - *チャンネル識別子* を上書きする
     - 文字列
     - None
     - チャンネル個別設定のセクション名は変わらない [#]_
   * - .. integrations_section:: separate
          :category: common

     - スコア入力元( *チャンネル識別子* )単位の集計
     - 真偽値
     - False
     - :True: 集計条件に *チャンネル識別子* を追加
   * - .. integrations_section:: plotting_backend
          :category: common

     - グラフ生成ライブラリ選択
     - 文字列
     - matplotlib
     - ``matplotlib`` / ``plotly`` から選択

..

.. danger::
   :integrations_section:`plotting_backend <common; plotting_backend>` は実装状況によってはデフォルト値から変更するとアプリケーションエラーとなり、正しく動作しなくなる。

.. rubric:: 脚注

.. [#] :setting_section:`channel_id` で使用するチャンネル識別子を変更している状態でもチャンネル個別設定のセクション名は ``<サービス名>_<チャンネルID>`` となる。


データベースファイル切替
------------------------

:integrations_section:`channel_config` でメイン設定の :setting_section:`database_file` が再定義できるため、別のDBファイルに情報を蓄積することが可能となる。

.. warning::
   以下の機能はDB切替実装が完了していないため、メイン設定にある :setting_section:`database_file` が利用される。

   - homeタブからの操作
   - `dbtools.py` によるDBメンテナンス

channel_id / separate について
------------------------------

:setting_section:`channel_id` / :setting_section:`separate` は以下の順序で定義内容を探索し、最初に未定義時の状態から変更されたものが設定値として採用される。

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

       - slack用 `slack-channel-settings`
       - discord用 `discord-channel-settings`
     - 指定チャンネルの範囲
   * - 3
     - `main-config`
     - `integrations-common`
     - 連携サービスの範囲
   * - 4
     - `main-config`
     - `setting-section`
     - アプリケーション全体(すべてのサービス、すべてのチャンネル)
