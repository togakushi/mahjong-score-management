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

   [results]
   command_suffix = 成績, サマリ

   [graph]
   command_suffix = グラフ

   [ranking]
   command_suffix = ランキング
   ranked = 10

   [report]
   command_suffix = レポート

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
