設定ファイル説明
================

アプリケーションの設定はツールの動作を定義する「 :ref:`main-config` (必須)」とルールセットを定義する「 :ref:`rule-config` (オプション)」から構成される。

| :ref:`main-config` 内にサービス個別の設定(slackやdiscordなど)が含まれる。
| サービス個別設定でチャンネル個別設定が定義されている場合は追加の設定ファイルが読み込まれる。

----

.. toctree::
   :caption: 設定内容
   :maxdepth: 2

   main/index
   rule/index
   example/index
