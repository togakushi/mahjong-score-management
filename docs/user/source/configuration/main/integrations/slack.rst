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
   * - :index:`slash_command <pair: slack section; slash_command>`
     - スラッシュコマンド名
     - 文字列
     - /mahjong
     - 先頭のスラッシュも含める
   * - :index:`thread_report <pair: slack section; thread_report>`
     - スレッド内にある *成績記録キーワード* を処理する
     - 真偽値
     - True
     -
   * - :index:`reaction_ok <pair: slack section; reaction_ok>`
     - 素点合計が正しい場合に付けるリアクション
     - 文字列(絵文字)
     - ok
     - ゲーム結果のポスト、メモに対して付く
   * - :index:`reaction_ng <pair: slack section; reaction_ng>`
     - 素点合計が誤っている場合に付けるリアクション
     - 文字列(絵文字)
     - ng
     - ゲーム結果のポストに対して付く
   * - :index:`ignore_userid <pair: slack section; ignore_userid>`
     - 投稿内容を無視するユーザID
     - 文字列
     - 空欄
     - 複数指定時はカンマ区切り
   * - :index:`channel_limitations <pair: slack section; channel_limitations>`
     - SQLを発行できるチャンネルID(カンマ区切り)
     - 文字列(channel_id)
     - None
     - 空欄(None)の場合はすべてのチャンネル
   * - :index:`comparison_word <pair: slack section; comparison_word>`
     - 突合処理呼び出しキーワード
     - 文字列
     - 麻雀チェック
     -
   * - :index:`comparison_alias <pair: slack section; comparison_alias>`
     - スラッシュコマンドエイリアス(突合処理呼び出しサブコマンド)
     - 文字列(カンマ区切り)
     - 空欄
     - サブコマンド ``check`` の別名を追加登録
   * - :index:`search_channel <pair: slack section; search_channel>`
     - 突合処理時に検索されるチャンネル名
     - 文字列(カンマ区切り)
     - 空リスト
     - チャンネル名に先頭の **#** は必要
   * - :index:`search_after <pair: slack section; search_after>`
     - データ突合開始日
     - 数値(int)
     - 7
     - 突合実行日時から指定日を引いた日を検索開始範囲にする
   * - :index:`search_wait <pair: slack section; search_wait>`
     - 突合処理待ち時間(秒)
     - 数値(int)
     - 180
     - イベント発生時刻から待ち時間以上経過したデータのみが突合の対象

.. tip::
   - ``ignore_userid`` は、botが出力する内容が検索にヒットしてしまう状況でbotのIDを指定するような利用方法を想定している。
   - ``channel_limitations`` は複数のチャンネルにbotをIntegrationsしている状態で、参照専用のチャンネルを作成するような利用方法を想定している。


.. _slack-channel-settings:

チャンネル個別設定
------------------

| メイン設定内に ``slack_<チャンネルID>`` セクションが存在すれば、そのチャンネル専用として追加で設定を読み込む。
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
   * - :index:`default_rule <pair: slack_channel section; default_rule>`
     - *ルール識別子* 未指定に使用するデフォルト値
     - 文字列
     - 引継
     - メイン設定の `setting-section` より優先される
   * - :index:`reaction_ok <pair: slack_channel section; reaction_ok>`
     - 素点合計が正しい場合に付けるリアクション
     - 文字列(絵文字)
     - 引継
     - `slack-section` の設定を上書き
   * - :index:`reaction_ng <pair: slack_channel section; reaction_ng>`
     - 素点合計が誤っている場合に付けるリアクション
     - 文字列(絵文字)
     - 引継
     - `slack-section` の設定を上書き
   * - :index:`search_channel <pair: slack_channel section; search_channel>`
     - 突合処理時に検索されるチャンネル
     - 文字列(チャンネル名)
     - 引継
     - `slack-section` の設定を上書き
   * - :index:`search_after <pair: slack_channel section; search_after>`
     - データ突合開始日
     - 数値(int)
     - 引継
     - `slack-section` の設定を上書き
