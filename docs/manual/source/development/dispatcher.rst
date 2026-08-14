ディスパッチャー
================

| 各機能はディスパッチテーブルから呼び出される。
| 呼び出される機能は `MessageParser <integrations.base.interface.MessageParserInterface>` を引数に取る。必要な情報は `data <integrations.base.interface.MessageParserInterface.data>` データクラスから取得する。

| 呼び出された機能はそれぞれ必要な処理を実施し、結果を `post <integrations.base.interface.MessageParserInterface.post>` データクラスと `status <integrations.base.interface.MessageParserInterface.status>` データクラスに保存する。
| サービス単位で後処理があるものは `FunctionsInterface <integrations.base.interface.FunctionsInterface>` の `post_processing() <integrations.base.interface.FunctionsInterface.post_processing>` で処理する。
