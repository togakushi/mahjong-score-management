トラブルシューティング & FAQ
============================

バックアップ / リストア
-----------------------

バックアップ
   使用しているDBファイル、INIファイルをすべてコピーする。

   - ファイルとして単純コピーすればよい
   - DBのcommit後はcloseしているので、アプリを止める必要はない

リストア
   退避したDBファイル、INIファイルを同じパスに保存し、アプリを再起動する。


データ修正
----------

登録したデータの時間を修正したい
   ゲーム結果のポストを誤って削除、あとから登録しなおした場合など。

   .. code-block:: sql
      :caption: 修正クエリ

      update result set ts = "修正したい時間", playtime = strftime("%Y-%m-%d %H:%M:%f", "修正したい時間", "unixepoch", "+9 hours") where ts = "入れなおした時間";

   時間は ``UnixEpoch`` で指定する。ミリ秒の桁数が足りないが、表示されない部分なので影響はない。

   .. danger:: 突合処理を動かすと Slack / Discord に記録されている時刻と異なるためデータベースの情報が更新される。


動作トラブル
------------

Slackのスラッシュコマンドが動かない

   .. code-block:: text
      :caption: Slackbot からの応答

      /slash_command failed with the error "dispatch_failed"

   アプリケーション設定（ `./setting/for_slack/setup` -> スラッシュコマンド有効化 ）と 設定ファイル（ `slack-section` の `slash_command <slash_command_slack>` ）が一致していない。
