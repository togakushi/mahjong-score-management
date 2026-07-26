.. _example-minimal:

最小構成
========

メイン設定
----------

| `main-config` に何も記述しない場合、すべてデフォルト値の状態で起動する。
| 設定される `ルールセット` 、コマンド呼び出しキーワードがわかればすぐに利用できる。

設定状況(アプリケーション起動ログから抜粋)
++++++++++++++++++++++++++++++++++++++++++

.. code-block:: text
   :caption: 使用データベースファイル

   [DEBUG][initialization:resultdb] /path/to/mahjong-score-management/mahjong.db

.. code-block:: text
   :caption: 呼び出しキーワード

   [DEBUG][configuration:register] keyword_dispatcher:
        成績集計: <function main at 0x7777dc5d6ac0>
        成績分析: <function main at 0x7777f8758fe0>
        麻雀ヘルプ: <function main at 0x7777dc15afc0>
        メンバー一覧: <function register.<locals>.dispatch_members_list at 0x777811901e40>
        チーム一覧: <function register.<locals>.dispatch_team_list at 0x7777dae3a200>

Slack / Discord を利用時は突合コマンドが追加される（ReminderはSlackのみ）。

.. code-block:: text
   :caption: 突合コマンド

        成績チェック: <function main at 0x7777db3531a0>
        Reminder: 成績チェック: <function main at 0x7777db3531a0>

.. code-block:: text
   :caption: スラッシュコマンド

   [DEBUG][configuration:register] command_dispatcher:
        member: <function register.<locals>.dispatch_members_list at 0x777811901e40>
        userlist: <function register.<locals>.dispatch_members_list at 0x777811901e40>
        member_list: <function register.<locals>.dispatch_members_list at 0x777811901e40>
        team_list: <function register.<locals>.dispatch_team_list at 0x7777dae3a200>
        download: <function register.<locals>.dispatch_download at 0x7777dafc4180>
        ダウンロード: <function register.<locals>.dispatch_download at 0x7777dafc4180>
        add: <function register.<locals>.dispatch_member_append at 0x7777f64e4540>
        del: <function register.<locals>.dispatch_member_remove at 0x7777dad18f40>
        team_create: <function register.<locals>.dispatch_team_create at 0x7777dad18e00>
        team_del: <function register.<locals>.dispatch_team_delete at 0x7777dad18ea0>
        team_add: <function register.<locals>.dispatch_team_append at 0x7777dad19120>
        team_remove: <function register.<locals>.dispatch_team_remove at 0x7777dad18fe0>
        team_clear: <function register.<locals>.dispatch_team_clear at 0x7777dad19080>


Slack / Discord を利用時は突合コマンドが追加される。

.. code-block:: text
   :caption: 突合コマンド

        check: <function main at 0x7777db3531a0>

.. code-block:: text
   :caption: 各セクション設定状況

   [DEBUG][configuration:setup] setting: {'remarks_suffix': [], 'rule_config': PosixPath('/home/togakushi/mahjong-score-management/files/default_rule.ini'), 'default_rule': 'default_rule', 'separate': False, 'channel_id': None, 'time_adjust': 12, 'search_word': '', 'group_length': 0, 'guest_mark': '※', 'database_file': PosixPath('mahjong.db'), 'backup_dir': None, 'font_file': PosixPath('/home/togakushi/mahjong-score-management/ipaexg.ttf'), 'graph_style': 'ggplot', 'work_dir': PosixPath('/home/togakushi/mahjong-score-management/work')}
   [DEBUG][configuration:setup] summary: {'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績集計'], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': []}
   [DEBUG][configuration:setup] analysis: {'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績分析'], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': []}
   [DEBUG][configuration:setup] member: {'commandword': ['メンバー一覧'], 'registration_limit': 255, 'character_limit': 8, 'alias_limit': 16, 'guest_name': 'ゲスト'}
   [DEBUG][configuration:setup] team: {'commandword': ['チーム一覧'], 'registration_limit': 255, 'character_limit': 16, 'member_limit': 16, 'friendly_fire': True}
   [DEBUG][configuration:setup] help: {'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['麻雀ヘルプ'], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': []}


サービス個別設定状況
++++++++++++++++++++

.. caution:: ``slash_command`` の不一致に注意！！

.. code-block:: text
   :caption: Slack

   [DEBUG][config:__post_init__] slack: SvcConfig(_parser=None, _command_dispatcher={}, _keyword_dispatcher={}, main_conf=<configparser.ConfigParser object at 0x7677712b29c0>, channel_config=None, slash_command='/mahjong', badge_degree=False, badge_status=False, badge_grade=False, separate=False, channel_id=None, plotting_backend='matplotlib', comparison_word='成績チェック', comparison_alias=[], search_channel=[], search_after=7, search_wait=180, thread_report=True, reaction_ok='ok', reaction_ng='ng', ignore_userid=[], channel_limitations=[], bot_id='', tab_var={})

.. code-block:: text
   :caption: Discord

   [DEBUG][config:__post_init__] discord: SvcConfig(_parser=None, _command_dispatcher={}, _keyword_dispatcher={}, main_conf=<configparser.ConfigParser object at 0x71527da66cc0>, channel_config=None, slash_command='mahjong', badge_degree=False, badge_status=False, badge_grade=False, separate=False, channel_id=None, plotting_backend='matplotlib', comparison_word='成績チェック', comparison_alias=[], search_after=7, ignore_userid=[], channel_limitations=[], bot_name=None)

.. code-block:: text
   :caption: Web

   [DEBUG][config:__post_init__] web: SvcConfig(_parser=None, _command_dispatcher={}, _keyword_dispatcher={}, main_conf=<configparser.ConfigParser object at 0x7fe607aa7560>, channel_config=None, slash_command='', badge_degree=False, badge_status=False, badge_grade=False, separate=False, channel_id=None, plotting_backend='plotly', host='', port=0, require_auth=False, username='', password='', use_ssl=False, certificate='', private_key='', view_summary=True, view_graph=True, view_ranking=True, view_report=True, management_member=False, management_score=False, theme='', custom_css='')


ルールセット設定
----------------

省略されているため  :manpage:`default_rule.ini` が読み込まれる。

.. code-block:: text
   :caption: ルールセット設定状況

   [INFO][rule:info] default_rule: mode=4, origin_point=250, return_point=300, rank_point=[30, 10, -10, -30], draw_split=False, ignore_flying=False, undefined_word=1
   [INFO][rule:info] default_rule3: mode=3, origin_point=350, return_point=400, rank_point=[30, 0, -30], draw_split=False, ignore_flying=False, undefined_word=1
   [INFO][rule:info] keyword_mapping: {'終局': 'default_rule'}
   [WARNING][rule:info] remarks_words: empty

`remarks_record` は使えない（未設定時は ``WARNING`` が出力される）。
