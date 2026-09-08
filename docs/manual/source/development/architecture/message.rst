出力メッセージ
==============

集計結果など各サービスへ出力される内容はすべて `PostData <integrations.protocols.PostData>` クラスで管理する。

表示させる内容は「 `MessageType <libs.types.MessageType>` （表示データ）」と「 `StyleOptions <libs.types.StyleOptions>` （表示オプション）」のペアのタプルで構成され、
`APIInterface.post() <integrations.base.interface.APIInterface.post>` を通して連携先サービスへ渡される。


MessageType
-----------

表示させるデータを保存する。
処理はデータの型を判別して行う。

.. list-table::
   :header-rows: 1
   :align: left
   :width: 70%

   * - データ型
     - 保存内容
     - 処理
   * - None
     - 空データ
     - なにもしない
   * - str
     - 整形済み文字データ
     - そのまま表示
   * - Path
     - ファイルパス
     - ファイルアップロード
   * - DataFrame
     - 表データ
     - テキストテーブルに変換して表示


StyleOptions
------------

表示させるデータに対するオプションを保存する。

実装は `APIInterface.post() <integrations.base.interface.APIInterface.post>` で行う。
データ生成プロセス側の要望をAPIに伝えるためのオプションとなる。

.. list-table::
   :header-rows: 1
   :align: left
   :width: 70%

   * - オプション
     - 内容
     - 概要
   * - title
     - タイトル文字列
     - 見出しとして表示する文字列を設定する
   * - key_title
     - タイトル表示フラグ
     - 見出しが不要な場合は ``False`` にセットする
   * - sub_title
     - サブタイトル化フラグ
     - :True: タイトルにコロンを追加して表示（タイトルとして使用）
       :False: タイトルを墨付き括弧で括って表示（見出しとして使用）
   * - codeblock
     - コードブロックとして表示する
     - ``True`` の場合はデータにコードブロック修飾を追加する
   * - indent
     - インデント指定
     - 指定数のTAB文字をデータの先頭に追加する
   * - RenameType
     - カラム名を変換するときの動作を変更する
     - :NONE: 変換しない
       :NORMAL: 通常変換
       :SHORT: 短縮変換
   * - その他
     -
     - `libs.types.StyleOptions` を参照


headline
--------

headline: tuple[MessageType, StyleOptions] | None = None

message
-------

message: list[tuple[MessageType, StyleOptions]]
