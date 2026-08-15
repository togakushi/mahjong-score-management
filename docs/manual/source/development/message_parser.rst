MessageParser仕様
=================

役割
   - 連携サービスからの入力を解析
   - 連携サービスへの出力データの保持

動作概要
   #. 連携サービスの入力イベント(ポスト/編集など)を `MsgData <integrations.protocols.MsgData>` に格納する
   #. `parser() <integrations.base.interface.MessageParserInterface.parser>` で入力イベントの内容を解析する
   #. `dispatcher.by_keyword() <libs.dispatcher.by_keyword>` が呼び出され、解析した `MsgData <integrations.protocols.MsgData>` の内容に従い処理を振り分ける
   #. コマンド処理の場合

      #. `analysis_argument() <libs.domain.command.CommandParser.analysis_argument>` が呼び出され、パラメータの内容を解析する
      #. 各処理の結果は `PostData <integrations.protocols.PostData>` に格納される

   #. `APIInterface.post() <integrations.base.interface.APIInterface.post>` が呼び出され、 `PostData <integrations.protocols.PostData>` の内容を連携サービスで出力する


MsgDataクラス
-------------

text
   入力されたテキスト全体を保存。


PostDataクラス
--------------

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

reaction
   入力元のイベントに対してリアクション文字を付与する際のフラグ。

action
   DBに対して発生した操作を示すフラグ。

result
   処理結果の状態。
