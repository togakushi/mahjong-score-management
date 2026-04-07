.. _slack-section:

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
   * - :index:`slash_command <single: integrations_slack; slash_command>`
     - スラッシュコマンド名
     - 文字列
     - /mahjong
     - 先頭のスラッシュも含める
   * - :index:`thread_report <single: integrations_slack; thread_report>`
     - スレッド内にある成績記録キーワードを処理する
     - 真偽値
     - True
     -
   * - :index:`reaction_ok <single: integrations_slack; reaction_ok>`
     - 素点合計が正しい場合に付けるリアクション
     - 文字列(絵文字)
     - ok
     - ゲーム結果のポスト、メモに対して付く
   * - :index:`reaction_ng <single: integrations_slack; reaction_ng>`
     - 素点合計が誤っている場合に付けるリアクション
     - 文字列(絵文字)
     - ng
     - ゲーム結果のポストに対して付く
   * - :index:`ignore_userid <single: integrations_slack; ignore_userid>`
     - 投稿内容を無視するユーザID
     - 文字列
     - 空欄
     - 複数指定時はカンマ区切り
   * - :index:`channel_limitations <single: integrations_slack; channel_limitations>`
     - SQLを発行できるチャンネルID(カンマ区切り)
     - 文字列(channel_id)
     - None
     - 空欄(None)の場合はすべてのチャンネル
   * - :index:`comparison_word <single: integrations_slack; comparison_word>`
     - 突合処理呼び出しキーワード
     - 文字列
     - 麻雀チェック
     -
   * - :index:`comparison_alias <single: integrations_slack; comparison_alias>`
     - スラッシュコマンドエイリアス(突合処理呼び出しサブコマンド)
     - 文字列(カンマ区切り)
     - 空欄
     - サブコマンド ``check`` の別名を追加登録
   * - :index:`search_channel <single: integrations_slack; search_channel>`
     - 突合処理時に検索されるチャンネル名
     - 文字列(カンマ区切り)
     - 空リスト
     - チャンネル名に先頭の **#** は必要
   * - :index:`search_after <single: integrations_slack; search_after>`
     - データ突合開始日
     - 数値(int)
     - 7
     - 突合実行日時から指定日を引いた日を検索開始範囲にする
   * - :index:`search_wait <single: integrations_slack; search_wait>`
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
| slackセクションの以下のキー、および共通設定の値を上書きする。

.. list-table::
   :width: 100%
   :widths: 15 30 15 15 40
   :header-rows: 1

   * - キー
     - 内容
     - 型
     - 未定義時
     - 備考
   * - :index:`default_rule <single: integrations_slack; default_rule>`
     - ルール識別子未指定に使用するデフォルト値
     - 文字列
     -
     - メイン設定の :ref:`setting-section` より優先される
   * - :index:`reaction_ok <single: integrations_slack; reaction_ok>`
     - 素点合計が正しい場合に付けるリアクション
     - 文字列(絵文字)
     - 引継
     - :ref:`slack-section` セクションの設定を上書き
   * - :index:`reaction_ng <single: integrations_slack; reaction_ng>`
     - 素点合計が誤っている場合に付けるリアクション
     - 文字列(絵文字)
     - 引継
     - :ref:`slack-section` セクションの設定を上書き
   * - :index:`search_channel <single: integrations_slack; search_channel>`
     - 突合処理時に検索されるチャンネル
     - 文字列(チャンネル名)
     - 引継
     - :ref:`slack-section` セクションの設定を上書き
   * - :index:`search_after <single: integrations_slack; search_after>`
     - データ突合開始日
     - 数値(int)
     - 引継
     - :ref:`slack-section` セクションの設定を上書き
