ベストプラクティス
==================

以下の要件を満たす設定ファイルの例

- 複数 `ルールセット`
- レギュレーション設定あり

メイン設定ファイル
------------------

.. code-block:: ini
   :caption: メイン設定

   [setting]
   rule_config = rule.ini
   remarks_suffix = メモ

   [summary]
   command_suffix = 成績, サマリ

   [analysis]
   command_suffix = 分析
   ranked = 10

   [help]
   command_suffix = ヘルプ


ルール設定ファイル
------------------

.. code-block:: ini
   :caption: ルール設定

   [league]
   keywords = 大会ルール
   mode = 4
   origin_point = 250
   return_point = 300
   rank_point = 30, 10, -10, -30
   draw_split = True
   ignore_flying = True
   undefined_word = 1

   [league_regulations]
   チョンボ = -20
   卓外清算 = -20

   [league_regulations_team]
   遅刻 = -50

   [practice]
   keywords = 練習ルール
   mode = 4
   origin_point = 250
   return_point = 300
   rank_point = 30, 10, -10, -30
   draw_split = False
   ignore_flying = False
   undefined_word = 1

   [practice_regulations]
   # 未定義とするため空セクション作成

   [practice_regulations_team]
   # 未定義とするため空セクション作成


コマンド呼び出しキーワード
--------------------------

各ルールセットの `keywords` と `各セクション <results_management>` の :sub_commands_section:`command_suffix` の組み合わせで生成される。

.. code-block:: text
   :caption: 組み合わせ結果

   大会ルール成績: <function main at 0x7edb56eeeac0>
   大会ルールサマリ: <function main at 0x7edb56eeeac0>
   練習ルール成績: <function main at 0x7edb56eeeac0>
   練習ルールサマリ: <function main at 0x7edb56eeeac0>
   大会ルール分析: <function main at 0x7edb732d0fe0>
   練習ルール分析: <function main at 0x7edb732d0fe0>
   大会ルールヘルプ: <function main at 0x7edb56d4efc0>
   練習ルールヘルプ: <function main at 0x7edb56d4efc0>
   メンバー一覧: <function register.<locals>.dispatch_members_list at 0x7edb710ac540>
   チーム一覧: <function register.<locals>.dispatch_team_list at 0x7edb55b79b20>

.. seealso:: `function-call-keyword`
