systemdを使ったデーモン化
=========================

実行環境準備
------------

.. note::
   【前提条件】セットアップ手順を実施し、スクリプトが起動できるようにする。

   - `../install/using_uv`
   - `../install/using_venv`

環境変数を記録したファイルを準備する( ``.env`` など)

.. code-block::
   :caption: 環境変数定義

   SLACK_APP_TOKEN=xapp-x-xxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SLACK_WEB_TOKEN=xoxp-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx


systemd設定
-----------

unitファイル作成
   ``/etc/systemd/system/python_app_slack.service`` を作成(ファイル名は好みでよい)

   .. code-block:: ini
      :caption: python_app_slack.service

      [Unit]
      Description=slack mahjong score management
      After=network.target

      [Service]
      User=<user name>
      Type=simple
      WorkingDirectory=/path/to/<app-dir>/
      EnvironmentFile=/path/to/<app-dir>/.env
      #ExecStartPre=git pull
      ExecStart=/path/to/<venv-dir>/bin/python3 /path/to/<app-dir>/app.py --notime
      #Restart=always

      [Install]
      WantedBy=default.target

   - ``User`` にスクリプトを起動するユーザ名を指定
   - ``WorkingDirectory`` に指定するディレクトリは`git clone`したときに作成したディレクトリ
   - ``/path/to/<venv-dir>/bin/python3`` は仮想環境のPython
   - ``/path/to/<app-dir>/.env`` は環境変数を記述したファイル
   - ``ExecStartPre`` 、 ``Restart`` はお好みで

unitファイル反映
   .. code-block:: shell
      :caption: daemon-reload

      $ sudo systemctl daemon-reload

自動起動有効化
   .. code-block:: shell
      :caption: enable

      $ sudo systemctl enable python_app_slack.service

起動/停止
   .. code-block:: shell
      :caption: start

      $ systemctl start python_app_slack.service

   .. code-block:: shell
      :caption: stop

      $ systemctl stop python_app_slack.service

ログ確認
   .. code-block:: shell
      :caption: status

      $ systemctl status python_app_slack.service -l --no-pager

   .. code-block:: shell
      :caption: journalctl

      $ journalctl -l -u python_app_slack.service --no-pager
