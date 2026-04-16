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

   [results]
   commandword = 成績サマリ, 成績サマリ2

   [graph]
   commandword = 成績グラフ, 成績グラフ2

   [ranking]
   commandword = 成績ランキング

   [report]
   commandword = 成績レポート

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

   [DEBUG][initialization:setup_resultdb] /path/to/mahjong-score-management/mahjong.db

.. code-block:: text
   :caption: 呼び出しキーワード

   [DEBUG][configuration:register] keyword_dispatcher:
           アプリヘルプ: <function register.<locals>.dispatch_help at 0x7feccc4093a0>
           成績サマリ: <function main at 0x7fecc8907560>
           成績サマリ2: <function main at 0x7fecc8907560>
           成績グラフ: <function main at 0x7fecc8d2aca0>
           成績グラフ2: <function main at 0x7fecc8d2aca0>
           成績ランキング: <function main at 0x7fecc8d55080>
           成績レポート: <function main at 0x7fecc8906520>
           部員リスト: <function register.<locals>.dispatch_members_list at 0x7fecc7672c00>
           チーム一覧: <function register.<locals>.dispatch_team_list at 0x7fecc76ed260>
           チーム構成: <function register.<locals>.dispatch_team_list at 0x7fecc76ed260>

Slack/Discordを利用時は突合コマンドが追加される。

.. code-block:: text
   :caption: 突合コマンド

           成績突合: <function main at 0x7fecc7a423e0>
           Reminder: 成績突合: <function main at 0x7fecc7a423e0>

.. code-block:: text
   :caption: スラッシュコマンド

   [DEBUG][configuration:register] command_dispatcher:
           results: <function main at 0x7fecc8907560>
           成績: <function main at 0x7fecc8907560>
           graph: <function main at 0x7fecc8d2aca0>
           グラフ: <function main at 0x7fecc8d2aca0>
           ranking: <function main at 0x7fecc8d55080>
           ランキング: <function main at 0x7fecc8d55080>
           report: <function main at 0x7fecc8906520>
           レポート: <function main at 0x7fecc8906520>
           member: <function register.<locals>.dispatch_members_list at 0x7fecc7672c00>
           userlist: <function register.<locals>.dispatch_members_list at 0x7fecc7672c00>
           member_list: <function register.<locals>.dispatch_members_list at 0x7fecc7672c00>
           メンバー: <function register.<locals>.dispatch_members_list at 0x7fecc7672c00>
           リスト: <function register.<locals>.dispatch_members_list at 0x7fecc7672c00>
           team_list: <function register.<locals>.dispatch_team_list at 0x7fecc76ed260>
           download: <function register.<locals>.dispatch_download at 0x7fecc7a65760>
           ダウンロード: <function register.<locals>.dispatch_download at 0x7fecc7a65760>
           add: <function register.<locals>.dispatch_member_append at 0x7fecc75dad40>
           追加: <function register.<locals>.dispatch_member_append at 0x7fecc75dad40>
           入部届: <function register.<locals>.dispatch_member_append at 0x7fecc75dad40>
           del: <function register.<locals>.dispatch_member_remove at 0x7fecc75dade0>
           削除: <function register.<locals>.dispatch_member_remove at 0x7fecc75dade0>
           退部届: <function register.<locals>.dispatch_member_remove at 0x7fecc75dade0>
           team_create: <function register.<locals>.dispatch_team_create at 0x7fecc75db060>
           team_del: <function register.<locals>.dispatch_team_delete at 0x7fecc75db100>
           team_add: <function register.<locals>.dispatch_team_append at 0x7fecc75db9c0>
           team_remove: <function register.<locals>.dispatch_team_remove at 0x7fecc75dba60>
           team_clear: <function register.<locals>.dispatch_team_clear at 0x7fecc75dbb00>
           help: <function command_help at 0x7fecc7a42980>

Slack/Discordを利用時は突合コマンドが追加される。

.. code-block:: text
   :caption: 突合コマンド

           check: <function main at 0x7fecc7a423e0>
           突合: <function main at 0x7fecc7a423e0>

.. code-block:: text
   :caption: 各セクション設定状況

   [DEBUG][section:config_load] mahjong: {'section': 'mahjong', 'mode': 4, 'rule_version': 'default_rule', 'origin_point': 250, 'return_point': 300, 'rank_point': [30, 10, -10, -30], 'ignore_flying': False, 'draw_split': False, 'undefined_word': 0, 'section_proxy': <Section: mahjong>}
   [DEBUG][section:config_load] setting: {'section': 'setting', 'keyword': '成績記録', 'remarks_word': 'ゲーム内メモ', 'remarks_suffix': [], 'rule_config': PosixPath('files/default_rule.ini'), 'time_adjust': 12, 'default_rule': '', 'separate': False, 'channel_id': None, 'search_word': '', 'group_length': 0, 'guest_mark': '※', 'database_file': PosixPath('mahjong.db'), 'backup_dir': None, 'font_file': PosixPath('ipaexg.ttf'), 'graph_style': 'ggplot', 'work_dir': PosixPath('work'), 'section_proxy': <Section: setting>}
   [DEBUG][section:config_load] alias: {'section': 'alias', 'results': ['results', '成績'], 'graph': ['graph', 'グラフ'], 'ranking': ['ranking', 'ランキング'], 'report': ['report', 'レポート'], 'download': ['download', 'ダウンロード', 'ダウンロード'], 'member': ['member', 'userlist', 'member_list', 'userlist', 'メンバー', 'リスト'], 'add': ['add', '追加', '入部届'], 'delete': ['del', '削除', '退部届'], 'team_create': ['team_create'], 'team_del': ['team_del'], 'team_add': ['team_add'], 'team_remove': ['team_remove'], 'team_list': ['team_list'], 'team_clear': ['team_clear'], 'section_proxy': <Section: alias>}
   [DEBUG][member:config_load] member: {'default_commandword': 'メンバー一覧', 'section': 'member', 'main_parser': <configparser.ConfigParser object at 0x710bc8d8abd0>, 'info': [], 'commandword': ['部員リスト'], 'command_suffix': [], 'registration_limit': 255, 'character_limit': 8, 'alias_limit': 16, 'guest_name': 'ゲスト', 'section_proxy': <Section: member>}
   [DEBUG][team:config_load] team: {'default_commandword': 'チーム一覧', 'section': 'team', 'main_parser': <configparser.ConfigParser object at 0x710bc8d8abd0>, 'info': [], 'commandword': ['チーム一覧', 'チーム構成'], 'command_suffix': [], 'registration_limit': 255, 'character_limit': 16, 'member_limit': 16, 'friendly_fire': True, 'section_proxy': <Section: team>}
   [DEBUG][section:config_load] results: {'default_commandword': '麻雀成績', 'section': 'results', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績サマリ', '成績サマリ2'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: results>}
   [DEBUG][section:config_load] graph: {'default_commandword': '麻雀グラフ', 'section': 'graph', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績グラフ', '成績グラフ2'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: graph>}
   [DEBUG][section:config_load] ranking: {'default_commandword': '麻雀ランキング', 'section': 'ranking', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績ランキング'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: ranking>}
   [DEBUG][section:config_load] report: {'default_commandword': '麻雀レポート', 'section': 'report', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['成績レポート'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: report>}
   [DEBUG][section:config_load] help: {'default_commandword': '麻雀ヘルプ', 'section': 'help', 'individual': True, 'guest_skip': True, 'guest_skip2': True, 'unregistered_replace': True, 'friendly_fire': False, 'statistics': False, 'ranked': 3, 'stipulated': 0, 'stipulated_rate': 0.05, 'interval': 80, 'search_word': '', 'group_length': 0, 'commandword': ['アプリヘルプ'], 'command_suffix': [], 'aggregation_range': '当日', 'always_argument': [], 'dropitems': [], 'section_proxy': <Section: help>}

定義した呼び出しキーワードは `commandword <commandword>` で確認できる。


サービス個別設定状況
++++++++++++++++++++

.. caution:: ``slash_command`` の不一致に注意！！

すべて省略しているので、 `minimal` と同じになる。

ルールセット設定
----------------

省略されているため :manpage:`default_rule.ini` が読み込まれる。

.. code-block:: text
   :caption: ルールセット登録状況

   [INFO][rule:info] keyword_mapping: {'成績記録': 'default_rule'}
   [INFO][rule:info] default_rule: mode=4, origin_point=250, return_point=300, rank_point=[30, 10, -10, 30], draw_split=False, ignore_flying=False
   [INFO][rule:info] default_rule3: mode=3, origin_point=350, return_point=400, rank_point=[30, 0, -30], draw_split=False, ignore_flying=False

`mahjong-section` で定義した `keywords <keywords>` とデフォルトルールとなる ``default_rule`` が紐付けられる。

三人打ちルールの ``default_rule3`` はルール定義をすべて省略すると登録されるがデフォルトルールには指定されない。
