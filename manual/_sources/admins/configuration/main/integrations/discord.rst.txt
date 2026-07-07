.. index::
   pair: メイン設定; discord section
   :name: discord-section

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
   * - .. integrations_section:: slash_command
          :category: discord section

     - スラッシュコマンド名
     - 文字列
     - mahjong
     - 先頭にスラッシュは不要
   * - .. integrations_section:: channel_limitations
          :category: discord section

     - SQLを発行できるチャンネル(カンマ区切り)
     - 文字列
     - None
     - - チャンネルID、チャンネル名で指定可
       - 空欄(None)の場合はすべてのチャンネル
   * - .. integrations_section:: comparison_word
          :category: discord section

     - 突合処理呼び出しキーワード
     - 文字列
     - 麻雀チェック
     -
   * - .. integrations_section:: comparison_alias
          :category: discord section

     - スラッシュコマンドエイリアス(突合処理呼び出しサブコマンド)
     - 文字列(カンマ区切り)
     - 空欄
     - サブコマンド ``check`` の別名を追加登録
   * - .. integrations_section:: search_after
          :category: discord section

     - データ突合開始日
     - 数値(int)
     - 7
     - 突合実行日時から指定日を引いた日を検索開始範囲にする

..

.. tip::
   botが参加してるチャンネルが複数ある場合、 :integrations_section:`channel_limitations <discord section; channel_limitations>` を指定することで成績登録ができるチャンネルを制限できる。

   サマリやグラフなどは制限されない。


.. _discord-channel-settings:

チャンネル個別設定
------------------

`main-config` 内に ``discord_<チャンネルID>セクション`` が存在すれば、そのチャンネル専用として追加で設定を読み込む。

`discord-section` の `integrations-common` の値を上書きする。
