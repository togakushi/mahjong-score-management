MessageParser
=============

役割
   | MessageParserは指定サービスから入力されたテキストデータをコマンドと引数に分ける役割を担う。
   | 状態を保持するためのデータクラスを3つ持つ。

   - MsgData
   - PostData
   - StatusData

動作概要
   #. 連携サービスの入力イベント(ポスト/編集など)を `MsgData <integrations.protocols.MsgData>` に格納する
   #. `MessageParserInterface.parser() <integrations.base.interface.MessageParserInterface.parser>` で入力イベントの内容を解析する
   #. `libs.dispatcher.by_keyword() <libs.dispatcher.by_keyword>` が呼び出され、解析した `MsgData <integrations.protocols.MsgData>` の内容に従い処理を振り分ける
   #. コマンド処理の場合

      #. `CommandParser.analysis_argument() <libs.domain.command.CommandParser.analysis_argument>` が呼び出され、パラメータの内容を解析する
      #. 各処理の結果は `PostData <integrations.protocols.PostData>` に格納される

   #. `APIInterface.post() <integrations.base.interface.APIInterface.post>` が呼び出され、 `PostData <integrations.protocols.PostData>` の内容を連携サービスで出力する


MsgDataクラス
-------------

入力されたテキストデータの情報を保持する。

- 入力テキスト
- イベント発生タイムスタンプ
- その他

text
   入力されたテキスト全体を保存。


PostDataクラス
--------------

各機能で集計した結果など、出力するデータを保持する。

- 集計結果
- 生成ファイル
- メッセージデータ
  - 集計期間などの補助情報
- その他

headline
   ヘッダメッセージとして返す内容。

   `MessageParser.set_headline() <integrations.protocols.MessageParserProtocol.set_headline>` を用いて値をセットする。

message
   | 本文メッセージとして返す内容。
   | リスト型になっており、複数の結果を保存可能。
   | 連携サービスへはリストの先頭から渡される。

   `MessageParser.set_message() <integrations.protocols.MessageParserProtocol.set_message>` を用いて値をセットする。


StatusDataクラス
----------------

各機能の最終的なステータス情報を保持する。

- DBに対する操作
- 更新したデータの状態
  - 矛盾したデータで更新した、など
- 処理結果
- その他

reaction
   入力元のイベントに対してリアクション文字を付与する際のフラグ。

action
   DBに対して発生した操作を示すフラグ。

result
   処理結果の状態。
