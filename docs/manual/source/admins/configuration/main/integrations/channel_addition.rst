.. _channel-addition:

チャンネル追加設定ファイル
==========================

`channel_config` で指定した設定ファイルを追加で読み込む。


パラメータのマージ
------------------

| `main-config` で定義している以下のセクションのパラメータはマージされる。
| それぞれのファイルに記述されている同名のセクションは、まとめてひとつのセクションとして扱われる。

- setting
- summary
- analysis


設定優先順序
++++++++++++

各パラメータは下記の順に探索され、最後に見つかった値が設定値として採用される。

#. `main-config` の各セクションのパラメータ
#. `channel-addition` の各セクションのパラメータ

`channel-addition` で定義されていないパラメータは `main-config` のパラメータを引き継ぐ。

.. important::
   `main-config` の各セクションの :sub_commands_section:`commandword` で指定されているキーワードは上書きできない。


メッセージカスタマイズ
----------------------

| `channel-addition` での `custom_message-section` の定義は `main-config` の内容をすべて上書きする。
| 未定義時は `main-config` の内容が引き継がれる。

.. important:: 一部だけの変更ではないことに注意。
