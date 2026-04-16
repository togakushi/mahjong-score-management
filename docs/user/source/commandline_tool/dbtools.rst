.. _dbtools.py:

dbtools.py
==========

.. program:: dbtools.py

概要
----

データベースファイルをメンテナンスする外部ツール

.. code-block:: shell
   :caption: 使い方

   $ uv run ./dbtools.py オプション

動作させる固有オプションを1つ指定する。

``config.ini`` で定義されているデータベースファイルが対象となる。

.. caution:: チャンネル個別設定で指定しているデータベースファイルは参照されない。


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
   :備考: 相対パス指定時は ``dbtools.py`` が起点になる

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


固有オプション
++++++++++++++

.. option:: --compar

   :内容: データ突合
   :省略時:
   :備考: ``--service`` で指定されている連携先と接続する

.. option:: --unification=UNIFICATION

   :内容: ファイルの内容に従って記録済みのメンバー名を修正する
   :省略時: rename.ini
   :備考: 書き換える内容はINIファイルに記述する

   メンバー登録済みの名前や利用不可能文字、登録禁止ワードなどが用いられている名前は書き換えから除外される。

   .. code-block:: ini
      :caption: INIファイル書式

      [rename]
      置き換え後の名前 = 置き換え前の名前, 置き換え前の名前, ...

.. option:: --recalculation

   :内容: ポイント再計算
   :省略時:
   :備考: 記録済みデータの素点からポイントを再計算する

   | DBからスコア情報を取り込み、定義済みの `ルールセット` と一致する `rule_version <rule_version>` であればその `ルールセット` の集計方法で再計算する。
   | 過去のデータを含め、すべてのレコードのポイントを再計算して更新する(変更点がなくても必ずupdateされる)。

.. option:: --export=PREFIX

   :内容: メンバー設定情報をエクスポート
   :省略時: export
   :備考:

   | エクスポートされたCSVファイルの1行目はヘッダ情報であり、インポートの際に必要となる。
   | ヘッダ情報は以下の通り。

   .. code-block::
      :caption: メンバーリスト (export_member.csv)

      name,slack_id,flying,reward,abuse,team_id

   ゲストを除いたメンバーのリスト。

   | ``team_id`` が空欄のメンバーはどのチームにも所属しない（未所属）。
   | 存在しないチームIDが指定されている場合は未所属扱いとなる。

   .. code-block::
      :caption: 別名リスト (export_alias.csv)

      name,member

   | ``name`` が別名、 ``member`` がメンバー名（表示される名前）となる。
   | 1行に1組のペアを記述する。

   .. code-block::
      :caption: 別名リスト (export_team.csv)

      id,name

.. option:: --import=PREFIX

   :内容: メンバー設定情報をインポート
   :省略時: export
   :備考:

   | PREFIXから始まるファイル名のCSVファイルからメンバー情報をインポートする。
   | メンバーリストのみ必須となる。

   メンバー情報はデータベースの情報を消去してからインポートされるため、ユーザーIDの欠番はなくなる。

.. option:: --vacuum

   :内容: データベースを最適化する
   :省略時:
   :備考:

.. option:: --gen-test-data=count

   :内容: テスト用サンプルデータ生成
   :省略時: 1
   :備考: count=生成回数

   | 動作確認用のテストデータを生成する。
   | 5人編成16チーム前提。総当たり戦。1countあたり455戦。

   .. seealso:: `../development/test`
