.. index::
   pair: メイン設定; slack section
   :name: slack-section

slackセクション
===============

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - .. integrations_section:: slash_command
          :category: slack section

     - スラッシュコマンド名
     - 文字列
     - /mahjong
     - 先頭のスラッシュも含める
   * - .. integrations_section:: thread_report
          :category: slack section

     - スレッド内にある *成績記録キーワード* を処理する
     - 真偽値
     - True
     -
   * - .. integrations_section:: reaction_ok
          :category: slack section

     - 素点合計が正しい場合に付けるリアクション
     - 文字列(絵文字)
     - ok
     - ゲーム結果のポスト、メモに対して付く
   * - .. integrations_section:: reaction_ng
          :category: slack section

     - 素点合計が誤っている場合に付けるリアクション
     - 文字列(絵文字)
     - ng
     - ゲーム結果のポストに対して付く
   * - .. integrations_section:: ignore_userid
          :category: slack section

     - 投稿内容を無視するユーザID
     - 文字列
     - 空欄
     - 複数指定時はカンマ区切り
   * - .. integrations_section:: channel_limitations
          :category: slack section

     - SQLを発行できるチャンネルID(カンマ区切り)
     - 文字列(channel_id)
     - None
     - 空欄(None)の場合はすべてのチャンネル
   * - .. integrations_section:: comparison_word
          :category: slack section

     - 突合処理呼び出しキーワード
     - 文字列
     - 麻雀チェック
     -
   * - .. integrations_section:: comparison_alias
          :category: slack section

     - スラッシュコマンドエイリアス(突合処理呼び出しサブコマンド)
     - 文字列(カンマ区切り)
     - 空欄
     - サブコマンド ``check`` の別名を追加登録
   * - .. integrations_section:: search_channel
          :category: slack section

     - 突合処理時に検索されるチャンネル名
     - 文字列(カンマ区切り)
     - 空リスト
     - チャンネル名に先頭の **#** は必要
   * - .. integrations_section:: search_after
          :category: slack section

     - データ突合開始日
     - 数値(int)
     - 7
     - 突合実行日時から指定日を引いた日を検索開始範囲にする
   * - .. integrations_section:: search_wait
          :category: slack section

     - 突合処理待ち時間(秒)
     - 数値(int)
     - 180
     - イベント発生時刻から待ち時間以上経過したデータのみが突合の対象

..

.. tip::
   - :integrations_section:`ignore_userid` は、botが出力する内容が検索にヒットしてしまう状況でbotのIDを指定するような利用方法を想定している。
   - :integrations_section:`channel_limitations <slack section; channel_limitations>` は複数のチャンネルにbotをIntegrationsしている状態で、参照専用のチャンネルを作成するような利用方法を想定している。


.. _slack-channel-settings:

チャンネル個別設定
------------------

| `main-config` 内に ``slack_<チャンネルID>`` セクションが存在すれば、そのチャンネル専用として追加で設定を読み込む。
| `slack-section` の以下のキー、および `integrations-common` の値を上書きする。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - .. integrations_section:: default_rule
          :category: slack_channel section

     - *ルール識別子* 未指定に使用するデフォルト値
     - 文字列
     - 引継
     - `main-config` の `setting-section` より優先される
   * - .. integrations_section:: reaction_ok
          :category: slack_channel section

     - 素点合計が正しい場合に付けるリアクション
     - 文字列(絵文字)
     - 引継
     - `slack-section` の設定を上書き
   * - .. integrations_section:: reaction_ng
          :category: slack_channel section

     - 素点合計が誤っている場合に付けるリアクション
     - 文字列(絵文字)
     - 引継
     - `slack-section` の設定を上書き
   * - .. integrations_section:: search_channel
          :category: slack_channel section

     - 突合処理時に検索されるチャンネル
     - 文字列(チャンネル名)
     - 引継
     - `slack-section` の設定を上書き
   * - .. integrations_section:: search_after
          :category: slack_channel section

     - データ突合開始日
     - 数値(int)
     - 引継
     - `slack-section` の設定を上書き
