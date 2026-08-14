インターフェース
================

.. mermaid::

   flowchart TB
       event(event handler);
       m1[["MessageParser(data)"]];

       event --> m1 --> d["dispatcher()"] --> f1 & f2 & f3;

       subgraph f1[Sub command]
           direction TB
           c([command]) --> sc1 & sc2 & sc3;
           sc1(summary) --> cp1[[CommandParser]] --> p1(aggregation);
           sc2(analysis) --> cp2[[CommandParser]] --> p2(aggregation);
           sc3(help) --> cp3[[CommandParser]] --> p3(text generation);
           p1 & p2 & p3 --> mp1[["MessageParser(post)<br>MessageParser(status)"]];
       end

       subgraph f2[Results record]
           direction TB
           r2([record]);
           r2 --> a1(score) --> results[(results)];
           r2 --> a2(remark) --> remarks[(remarks)];
           results & remarks --> pp2["post_processing()"] --> mp2[["MessageParser(post)<br>MessageParser(status)"]];
       end

       subgraph f3[Member management]
           direction TB
           r1([registry]);
           r1 --> a4(team) --> db2[(team)] & db1;
           r1 --> a3(member) --> db1[(member)] & db3[(alias)];
           r1 --> a5(alias) --> db3;
           db1 & db2 & db3  --> mp3[["MessageParser(post)<br>MessageParser(status)"]];
       end

       f1 & f2 & f3 --> post["post()<br>(API Interface)"];

..
   ---
   config:
     flowchart:
       curve: linear
   ---

アダプタ
========

| アプリ起動時に指定されたサービスのアダプタが設定される。
| アダプタは以下のクラスを含む抽象化されたクラスである。

- IntegrationsConfig
- APIInterface
- FunctionsInterface
- MessageParser

.. admonition:: 関係図
   :collapsible: closed

   .. mermaid::

      classDiagram
          class ServiceAdapter
              ServiceAdapter : interface_type
              ServiceAdapter --* IntegrationsConfig
              ServiceAdapter --* APIInterface
              ServiceAdapter --* FunctionsInterface
              ServiceAdapter --* MessageParser

          class IntegrationsConfig
              IntegrationsConfig : config_file
              IntegrationsConfig : slash_command
              IntegrationsConfig : badge_degree
              IntegrationsConfig : badge_status
              IntegrationsConfig : badge_grade
              IntegrationsConfig : plotting_backend
              IntegrationsConfig : read_file()

          class APIInterface
              APIInterface : post()

          class FunctionsInterface
              FunctionsInterface : post_processing()
              FunctionsInterface : get_conversations()

          class MessageParser
              MessageParser : data
              MessageParser : post
              MessageParser : status
              MessageParser : parser()

          class MessageParserDataMixin
              MessageParserDataMixin <|-- MessageParser
              MessageParserDataMixin : data
              MessageParserDataMixin : post
              MessageParserDataMixin : status
              MessageParserDataMixin : reset()
              MessageParserDataMixin : get_remarks()


IntegrationsConfig
------------------

| 指定サービスのみで利用する設定値を保存する。
| 設定値は設定ファイルのサービス名と同じセクションに記述する。


APIInterface
------------

| 指定サービスに対して出力を行う。
| 出力する内容は `MessageParser <integrations.base.interface.MessageParserInterface>` の `post <integrations.base.interface.MessageParserInterface.post>` データクラスが保持している。


FunctionsInterface
------------------

| 指定サービスに対するサービス専用の関数群。
| `APIInterface <integrations.base.interface.APIInterface>` 、 `MessageParser <integrations.base.interface.MessageParserInterface>` から利用される。


MessageParser
-------------

| MessageParserは指定サービスから入力されたテキストデータをコマンドと引数に分ける役割を担う。
| 状態を保持するためのデータクラスを3つ持つ。

- data
- post
- status

data
   入力されたテキストデータの情報を保持する。

   - 入力テキスト
   - イベント発生タイムスタンプ
   - その他

post
   各機能で集計した結果など、出力するデータを保持する。

   - 集計結果
   - 生成ファイル
   - メッセージデータ
     - 集計期間などの補助情報
   - その他

status
   各機能の最終的なステータス情報を保持する。

   - DBに対する操作
   - 更新したデータの状態
     - 矛盾したデータで更新した、など
   - 処理結果
   - その他
