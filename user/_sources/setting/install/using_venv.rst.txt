venvを使った実行環境構築
========================

Python3.12以上の実行環境が必要なため、OS環境に合わせて準備する。

.. tip:: Pythonのインストールが必要な環境なのであれば :doc:`using_uv` がおすすめ。

本体インストール
----------------

.. code-block:: shell
   :caption: git clone

   $ git clone https://github.com/togakushi/mahjong-score-management.git


仮想環境の作成
--------------

作成するディレクトリ名は任意。

.. code-block:: shell
   :caption: 仮想環境作成

   $ python3 -m venv venvdir
   $ source ./venvdir/bin/activate

.. code-block:: shell
   :caption: 依存パッケージのインストール

   (venvdir) $ cd slack-mahjong-score-management
   (venvdir) $ pip install -U pip
   (venvdir) $ pip install -r requirements.txt


グラフ描写用の日本語フォント
----------------------------

IPAexフォント（ipaexg.ttf）を `app.py` と同じディレクトリに配置

- https://moji.or.jp/ipafont/ipafontdownload/


環境変数
--------

発行されたトークンを環境変数にセット

.. code-block:: shell
   :caption: Slack利用時

   $ export SLACK_APP_TOKEN=xapp-x-xxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   $ export SLACK_WEB_TOKEN=xoxp-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   $ export SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx

.. code-block:: shell
   :caption: Discord利用時

   $ export DISCORD_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


起動
----

.. code-block:: shell
   :caption: 通常起動

   (venvdir) $ python3 app.py

もしくは、

.. code-block:: shell
   :caption: 通常起動

   (venvdir) $ chmod u+x app.py
   (venvdir) $ ./app.py


.. code-block:: shell
   :caption:  バックグラウンド起動

   (venvdir) $ nohup python3 ./app.py > /dev/null 2>&1 &


停止
----

PIDを調べてプロセスをkill。
