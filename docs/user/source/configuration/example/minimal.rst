.. _example-minimal:

最小構成
========

メイン設定
----------

| `main-config` に何も記述しない場合、すべてデフォルト値の状態で起動する。
| 設定される `ルールセット` 、機能呼び出しキーワードがわかればすぐに利用できる。

設定状況(アプリケーション起動ログから抜粋)
++++++++++++++++++++++++++++++++++++++++++

.. code-block:: text
   :caption: 使用データベースファイル

   [DEBUG][initialization:setup_resultdb] /path/to/mahjong-score-management/mahjong.db

.. code-block:: text
   :caption: 呼び出しキーワード

   [DEBUG][configuration:register] keyword_dispatcher:
           麻雀成績: <function main at 0x7298ffe2c220>
           麻雀グラフ: <function main at 0x729901da3240>
           麻雀ランキング: <function main at 0x7298ffddb560>
           麻雀レポート: <function main at 0x7298ffddba60>
           麻雀ヘルプ: <function main at 0x7298ffddb380>
           メンバー一覧: <function register.<locals>.dispatch_members_list at 0x7298fe9d7e20>
           チーム一覧: <function register.<locals>.dispatch_team_list at 0x7298fe9d7ec0>

Slack / Discord を利用時は突合コマンドが追加される（ReminderはSlackのみ）。

.. code-block:: text
   :caption: 突合コマンド

           成績チェック: <function main at 0x7c37e0e7ec00>
           Reminder: 成績チェック: <function main at 0x7c37e0e7ec00>

.. code-block:: text
   :caption: スラッシュコマンド

   [DEBUG][configuration:register] command_dispatcher:
           results: <function main at 0x7298ffe2c220>
           成績: <function main at 0x7298ffe2c220>
           graph: <function main at 0x729901da3240>
           グラフ: <function main at 0x729901da3240>
           ranking: <function main at 0x7298ffddb560>
           ランキング: <function main at 0x7298ffddb560>
           report: <function main at 0x7298ffddba60>
           レポート: <function main at 0x7298ffddba60>
           member: <function register.<locals>.dispatch_members_list at 0x7298fe9d7e20>
           userlist: <function register.<locals>.dispatch_members_list at 0x7298fe9d7e20>
           member_list: <function register.<locals>.dispatch_members_list at 0x7298fe9d7e20>
           team_list: <function register.<locals>.dispatch_team_list at 0x7298fe9d7ec0>
           download: <function register.<locals>.dispatch_download at 0x72991b3822a0>
           ダウンロード: <function register.<locals>.dispatch_download at 0x72991b3822a0>
           add: <function register.<locals>.dispatch_member_append at 0x7298fe9d7880>
           del: <function register.<locals>.dispatch_member_remove at 0x7298fea0c040>
           team_create: <function register.<locals>.dispatch_team_create at 0x7298fea0c0e0>
           team_del: <function register.<locals>.dispatch_team_delete at 0x7298fea0c180>
           team_add: <function register.<locals>.dispatch_team_append at 0x7298fea0c220>
           team_remove: <function register.<locals>.dispatch_team_remove at 0x7298fea0c2c0>
           team_clear: <function register.<locals>.dispatch_team_clear at 0x7298fea0c360>


Slack / Discord を利用時は突合コマンドが追加される。

.. code-block:: text
   :caption: 突合コマンド

           check: <function main at 0x7c37e0e7ec00>

.. code-block:: text
   :caption: 各セクション設定状況

   [DEBUG][section:config_load] mahjong: {'section': 'mahjong', 'mode': 4, 'rule_version': 'default_rule', 'origin_point': 250, 'return_point': 300, 'rank_point': [30, 10, -10, -30], 'ignore_flying': False, 'draw_split': False, 'undefined_word': 0, 'section_proxy': <Section: mahjong>}
   [DEBUG][section:config_load] setting: {'section': 'setting', 'keyword': '終局', 'remarks_word': '麻雀メモ', 'remarks_suffix': [], 'rule_config': PosixPath('files/default_rule.ini'), 'time_adjust': 12, 'default_rule': '', 'separate': False, 'channel_id': None, 'search_word': '', 'group_length': 0, 'guest_mark': '※', 'database_file': PosixPath('mahjong.db'), 'backup_dir': None, 'font_file': PosixPath('ipaexg.ttf'), 'graph_style': 'ggplot', 'work_dir': PosixPath('work'), 'section_proxy': <Section: setting>}
   [DEBUG][section:config_load] alias: {'section': 'alias', 'results': ['results', '成績'], 'graph': ['graph', 'グラフ'], 'ranking': ['ranking', 'ランキング'], 'report': ['report', 'レポート'], 'download': ['download', 'ダウンロード'], 'member': ['member', 'userlist', 'member_list'], 'add': ['add'], 'delete': ['del', 'del'], 'team_create': ['team_create'], 'team_del': ['team_del'], 'team_add': ['team_add'], 'team_remove': ['team_remove'], 'team_list': ['team_list'], 'team_clear': ['team_clear'], 'section_proxy': <Section: alias>}
   [DEBUG][member:config_load] member: {'default_commandword': 'メンバー一覧', 'section': 'member', 'main_parser': <configparser.ConfigParser object at 0x74cd09a485f0>, 'info': [], 'commandword': ['メンバー一覧'], 'command_suffix': [], 'registration_limit': 255, 'character_limit': 8, 'alias_limit': 16, 'guest_name': 'ゲスト', 'section_proxy': <Section: member>}
   [DEBUG][team:config_load] team: {'default_commandword': 'チーム一覧', 'section': 'team', 'main_parser': <configparser.ConfigParser object at 0x74cd09a485f0>, 'info': [], 'commandword': ['チーム一覧'], 'command_suffix': [], 'registration_limit': 255, 'character_limit': 16, 'member_limit': 16, 'friendly_fire': True, 'section_proxy': <Section: team>}
   [DEBUG][section:config_load] results: {'default_commandword': '麻雀成績', 'section': 'results', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['麻雀成績'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: results>}
   [DEBUG][section:config_load] graph: {'default_commandword': '麻雀グラフ', 'section': 'graph', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['麻雀グラフ'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: graph>}
   [DEBUG][section:config_load] ranking: {'default_commandword': '麻雀ランキング', 'section': 'ranking', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['麻雀ランキング'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: ranking>}
   [DEBUG][section:config_load] report: {'default_commandword': '麻雀レポート', 'section': 'report', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['麻雀レポート'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: report>}
   [DEBUG][section:config_load] help: {'default_commandword': '麻雀ヘルプ', 'section': 'help', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['麻雀ヘルプ'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: help>}


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
   :caption: ルールセット登録状況

   [INFO][rule:info] keyword_mapping: {'終局': 'default_rule'}
   [INFO][rule:info] default_rule: mode=4, origin_point=250, return_point=300, rank_point=[30, 10, -10, -30], draw_split=False, ignore_flying=False
   [INFO][rule:info] default_rule3: mode=3, origin_point=350, return_point=400, rank_point=[30, 0, -30], draw_split=False, ignore_flying=False
