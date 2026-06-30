.. _example-ruleset:

ルールセット設定例
==================

ルールセット設定
----------------

以下を *rule.ini* に定義し、 `rule_config` で指定する。

.. code-block:: ini
   :caption: rule.ini

   [麻雀部ルール]
   keywords = 成績記録
   rank_point = 20, 10, -10, -20

   [リーグ戦ルール]
   mode = 4
   origin_point = 250
   return_point = 300
   rank_point = 30, 10, -10, -30
   draw_split = True
   ignore_flying = True

   [サンマルール]
   mode = 3
   rank_point = 20, 0, -20


メイン設定パターン別のルールセット登録状況の説明
------------------------------------------------

.. tip::
   `ルールセット` 以外の設定状況については他の設定事例を参照。


追加設定なし
++++++++++++

.. code-block:: ini
   :caption: メイン設定

   [setting]
   rule_config = rule.ini


.. code-block:: text
   :caption: ルールセット登録状況

   [INFO][rule:info] keyword_mapping: {'成績記録': '麻雀部ルール'}
   [INFO][rule:info] 麻雀部ルール: mode=4, origin_point=250, return_point=300, rank_point=[20, 10, -10, -20], draw_split=False, ignore_flying=False
   [INFO][rule:info] リーグ戦ルール: mode=4, origin_point=250, return_point=300, rank_point=[30, 10, -10, -30], draw_split=True, ignore_flying=True
   [INFO][rule:info] サンマルール: mode=3, origin_point=350, return_point=400, rank_point=[20, 0, -20], draw_split=False, ignore_flying=False
