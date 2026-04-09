.. _app.py:

app.py
======

.. program:: app.py

概要
----

メインスクリプト


コマンドライン引数
------------------

共通オプション
++++++++++++++

.. option:: -h, --help

   :内容: ヘルプ表示
   :省略時:
   :備考:

.. option:: -c CONFIG, --config=CONFIG

   :内容: 設定ファイル
   :省略時: config.ini
   :備考: 相対パス指定時は ``app.py`` が起点になる

.. option:: --service=SERVICE_NAME

   :内容: 連携先サービス
   :省略時: slack
   :備考: - slack
          - discord
          - standard_io, std
          - web, flask


ロギングオプション
++++++++++++++++++

.. option:: -d, --debug

   :内容: | デバッグレベル
          | 1: debug
          | 2: trace
   :省略時: 0
   :備考:

.. option:: -v, --verbose

   :内容: | 動作ログ出力切替
          | 1 (0x01): パラメータ&クエリ
          | 2 (0x02): クエリ実行結果
          | 3 (0x03): 両方出力
   :省略時: 0
   :備考:

.. option:: --moderate

   :内容: ログレベルがエラー以下のもを非表示
   :省略時: False
   :備考:

.. option:: --notime

   :内容: ログフォーマットから日時を削除
   :省略時: False
   :備考:


個別オプション(standard_io専用)
+++++++++++++++++++++++++++++++

.. option:: --text

   :内容: 呼び出しキーワードを指定
   :省略時:
   :備考: 空白区切りで引数も指定可能


個別オプション(web専用)
+++++++++++++++++++++++

.. option:: --host

   :内容: 起動するアドレス
   :省略時: 127.0.0.1
   :備考:

.. option:: --port

   :内容: 起動するポート
   :省略時: 8000
   :備考:
