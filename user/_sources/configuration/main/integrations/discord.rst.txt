discordセクション
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
   * - :index:`slash_command <single: integrations_discord; slash_command>`
     - スラッシュコマンド名
     - 文字列
     - mahjong
     - 先頭にスラッシュは不要
   * - :index:`channel_limitations <single: integrations_discord; channel_limitations>`
     - SQLを発行できるチャンネル(カンマ区切り)
     - 文字列
     - None
     - - チャンネルID、チャンネル名で指定可
       - 空欄(None)の場合はすべてのチャンネル
   * - :index:`comparison_word <single: integrations_discord; comparison_word>`
     - 突合処理呼び出しキーワード
     - 文字列
     - 麻雀チェック
     -
   * - :index:`comparison_alias <single: integrations_discord; comparison_alias>`
     - スラッシュコマンドエイリアス(突合処理呼び出しサブコマンド)
     - 文字列(カンマ区切り)
     - 空欄
     - サブコマンド ``check`` の別名を追加登録
   * - :index:`search_after <single: integrations_discord; search_after>`
     - データ突合開始日
     - 数値(int)
     - 7
     - 突合実行日時から指定日を引いた日を検索開始範囲にする

.. tip::
   | botが参加してるチャンネルが複数ある場合、 ``channel_limitations`` を指定することで成績登録ができるチャンネルを制限できる。
   | サマリやグラフなどは制限されない。


.. _discord-channel-settings:

チャンネル個別設定
------------------

メイン設定内に ``discord_<チャンネルID>セクション`` が存在すれば、そのチャンネル専用として追加で設定を読み込む。

discordセクションの共通設定の値を上書きする。
