呼び出しコマンド定義
====================

メイン設定
----------

コマンド名の設定を行う。

.. code-block:: ini
   :caption: メイン設定

   [setting]
   keyword = 成績記録
   remarks_word = ゲーム内メモ

   [alias] # 一部のみ指定
   download = ダウンロード
   member = userlist, メンバー, リスト
   add = 追加, 入部届
   del = 削除, 退部届

   [summary]
   commandword = 成績サマリ, 成績サマリ2

   [analysis]
   commandword = 成績分析, 成績分析2

   [member]
   commandword = 部員リスト

   [team]
   commandword = チーム一覧, チーム構成

   [help]
   commandword = アプリヘルプ

   [slack]
   comparison_word = 成績突合
   comparison_alias = 突合

   [discord]
   comparison_word = 成績突合
   comparison_alias = 突合


設定状況(アプリケーション起動ログから抜粋)
++++++++++++++++++++++++++++++++++++++++++

.. code-block:: text
   :caption: 使用データベースファイル

   [DEBUG][initialization:resultdb] /path/to/mahjong-score-management/mahjong.db

.. code-block:: text
   :caption: 呼び出しキーワード

   [DEBUG][configuration:register] keyword_dispatcher:
        成績サマリ: <function main at 0x7a314eb32f20>
        成績サマリ2: <function main at 0x7a314eb32f20>
        成績分析: <function main at 0x7a316b0d5300>
        成績分析2: <function main at 0x7a316b0d5300>
        アプリヘルプ: <function main at 0x7a316b0d14e0>
        部員リスト: <function register.<locals>.dispatch_members_list at 0x7a3168e60ae0>
        チーム一覧: <function register.<locals>.dispatch_team_list at 0x7a314d9289a0>
        チーム構成: <function register.<locals>.dispatch_team_list at 0x7a314d9289a0>

Slack / Discord を利用時は突合コマンドが追加される。

.. code-block:: text
   :caption: 突合コマンド

        成績突合: <function main at 0x7be0a42cb1a0>
        Reminder: 成績突合: <function main at 0x7be0a42cb1a0>

.. code-block:: text
   :caption: スラッシュコマンド

   [DEBUG][configuration:register] command_dispatcher:
        member: <function register.<locals>.dispatch_members_list at 0x7be0a3f1db20>
        userlist: <function register.<locals>.dispatch_members_list at 0x7be0a3f1db20>
        member_list: <function register.<locals>.dispatch_members_list at 0x7be0a3f1db20>
        メンバー: <function register.<locals>.dispatch_members_list at 0x7be0a3f1db20>
        リスト: <function register.<locals>.dispatch_members_list at 0x7be0a3f1db20>
        team_list: <function register.<locals>.dispatch_team_list at 0x7be0da865e40>
        download: <function register.<locals>.dispatch_download at 0x7be0a3f3ea20>
        ダウンロード: <function register.<locals>.dispatch_download at 0x7be0a3f3ea20>
        add: <function register.<locals>.dispatch_member_append at 0x7be0bf46c540>
        追加: <function register.<locals>.dispatch_member_append at 0x7be0bf46c540>
        入部届: <function register.<locals>.dispatch_member_append at 0x7be0bf46c540>
        del: <function register.<locals>.dispatch_member_remove at 0x7be0a3c94fe0>
        削除: <function register.<locals>.dispatch_member_remove at 0x7be0a3c94fe0>
        退部届: <function register.<locals>.dispatch_member_remove at 0x7be0a3c94fe0>
        team_create: <function register.<locals>.dispatch_team_create at 0x7be0a3c94ea0>
        team_del: <function register.<locals>.dispatch_team_delete at 0x7be0a3c94f40>
        team_add: <function register.<locals>.dispatch_team_append at 0x7be0a3c951c0>
        team_remove: <function register.<locals>.dispatch_team_remove at 0x7be0a3c95080>
        team_clear: <function register.<locals>.dispatch_team_clear at 0x7be0a3c95120>

Slack / Discord を利用時は突合コマンドが追加される。

.. code-block:: text
   :caption: 突合コマンド

        check: <function main at 0x7be0a42cb1a0>
        突合: <function main at 0x7be0a42cb1a0>

.. code-block:: text
   :caption: 各セクション設定状況

   [DEBUG][configuration:setup] setting: {'remarks_suffix': [], 'rule_config': PosixPath('/home/togakushi/mahjong-score-management/files/default_rule.ini'), 'default_rule': 'default_rule', 'separate': False, 'channel_id': None, 'time_adjust': 12, 'search_word': '', 'group_length': 0, 'guest_mark': '※', 'database_file': PosixPath('mahjong.db'), 'backup_dir': None, 'font_file': PosixPath('/home/togakushi/mahjong-score-management/ipaexg.ttf'), 'graph_style': 'ggplot', 'work_dir': PosixPath('/home/togakushi/mahjong-score-management/work')}
   [DEBUG][configuration:setup] summary: {'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績サマリ', '成績サマリ2'], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': []}
   [DEBUG][configuration:setup] analysis: {'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績分析', '成績分析2'], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': []}
   [DEBUG][configuration:setup] member: {'commandword': ['部員リスト'], 'registration_limit': 255, 'character_limit': 8, 'alias_limit': 16, 'guest_name': 'ゲスト'}
   [DEBUG][configuration:setup] team: {'commandword': ['チーム一覧', 'チーム構成'], 'registration_limit': 255, 'character_limit': 16, 'member_limit': 16, 'friendly_fire': True}
   [DEBUG][configuration:setup] help: {'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['アプリヘルプ'], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': []}

定義した呼び出しキーワードは :sub_commands_section:`commandword` で確認できる。


サービス個別設定状況
++++++++++++++++++++

.. caution:: ``slash_command`` の不一致に注意！！

すべて省略しているので、 `example-minimal` と同じになる。

ルールセット設定
----------------

省略されているため :manpage:`default_rule.ini` が読み込まれる。

.. code-block:: text
   :caption: ルールセット登録状況

   [INFO][rule:info] keyword_mapping: {'成績記録': 'default_rule'}
   [INFO][rule:info] default_rule: mode=4, origin_point=250, return_point=300, rank_point=[30, 10, -10, 30], draw_split=False, ignore_flying=False
   [INFO][rule:info] default_rule3: mode=3, origin_point=350, return_point=400, rank_point=[30, 0, -30], draw_split=False, ignore_flying=False

`mahjong-section` で定義した `keywords` とデフォルトルールとなる ``default_rule`` が紐付けられる。

三人打ちルールの ``default_rule3`` はルール定義をすべて省略すると登録されるがデフォルトルールには指定されない。
