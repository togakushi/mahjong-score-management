# MessageParser仕様
## 役割
- 連携サービスからの入力を解析
- 連携サービスへの出力データの保持

### 動作概要
1. 連携サービスの入力イベント(ホスト/編集など)をトリガーに`parser()`を呼び出す
2. `parser()`は発生イベントの内容を解析し、結果を`MsgData`に格納する
3. `dispatcher.by_keyword()`が呼び出され、`MsgData`の内容に従い処理を振り分ける
4. 各処理の結果は`PostData`に格納される
5. `post()`が呼び出され、`PostData`の内容を連携サービスで出力する

## MsgData
### text
入力されたテキスト全体を保存。

## PostData
### headline
ヘッダメッセージとして返す内容。

`MessageParser.set_headline()`を用いて値をセットする。

### message
本文メッセージとして返す内容。</br>
リスト型になっており、複数の結果を保存可能。</br>
連携サービスへはリストの先頭から渡される。

`MessageParser.set_message()`を用いて値をセットする。

## StatusData
### reaction
入力元のイベントに対してリアクション文字を付与する際のフラグ。

### action
DBに対して発生した操作を示すフラグ。

### result
処理結果の状態。
