アダプタ
========

| アプリ起動時に指定されたサービスのアダプタが設定される。
| アダプタは以下のクラスを含む抽象化されたクラスである。

   .. toctree::
      :maxdepth: 1

      integrations_config
      api_interface
      functions_interface
      message_parser

関係図
------

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
