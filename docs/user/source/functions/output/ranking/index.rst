.. _function-ranking:

ランキング生成
==============

記録された成績データを集計し、ランキングを作成する。


構文
----

:チャンネル内呼び出し: <呼び出しキーワード> [オプション]
:スラッシュコマンド: /commandname ranking [オプション]

.. note::
   ``/commandname`` は以下で定義する

   - `slack-section` の :integrations_section:`slash_command <slack section; slash_command>`
   - `discord-section` の :integrations_section:`slash_command <discord section; slash_command>`


オプション
----------

基本オプション
++++++++++++++

.. ranking:: メンバー名, チーム名
   :category: 基本オプション

   指定メンバー / チームだけでランキングを生成する。


個別オプション
++++++++++++++

.. ranking:: トップ<NNN>, top<NNN>
   :category: 個別オプション

   上位NNN位まで出力。

.. ranking:: レート, レーティング, rating
   :category: 個別オプション

   レーティングを表示。

.. ranking:: 比較, 点差, 差分
   :category: 個別オプション

   ゲーム終了時の素点情報の表示

   :平均素点: ゲーム終了時点の素点平均
   :x位偏差: x位獲得時の偏差（平均-全体平均）


共通オプション
++++++++++++++

- `common-options`


項目説明
--------

ランキング
++++++++++

.. glossary::

   通算ポイント : ランキング項目
      ウマ、オカを足して最終得点を確定させて算出したポイントの合計。

   平均ポイント : ランキング項目
      通算ポイントを対戦数で割ったもの。

   平均収支 : ランキング項目
      各ゲームの「素点-配給原点」の平均点を出したもの。

   トップ率 : ランキング項目
      トップ（1位）を取った回数/対戦数。

   連対率 : ランキング項目
      | 連対（1位と2位）を取った回数/対戦数。
      | 順位点がプラスの着順を取ってる率。

   ラス回避率 : ランキング項目
      4着以外（1位と2と3位）を取った回数/対戦数。

   トビ率 : ランキング項目
      | 素点がマイナスになった率。
      | トビにくいプレイヤーが上位。

   平均順位 : ランキング項目
      | 獲得着順を対戦数で割った平均値。
      | 2.5が基準。小さいほうが優秀。


レーティング
++++++++++++

.. glossary::

   レート : レーティング項目
      獲得順位から計算したレーティング。初期値は1500。

   順位偏差 : レーティング項目
      集計集団の中の平均順位の偏差。

   得点偏差 : レーティング項目
      集計集団の中の平均素点(ゲーム終了時点の持ち点)の偏差。


出力サンプル
------------

.. admonition:: 個人ランキング
   :collapsible: closed

   .. literalinclude:: sample_ranking_individual.txt

.. admonition:: チームランキング
   :collapsible: closed

   .. literalinclude:: sample_ranking_team.txt

.. admonition:: チームレーティング
   :collapsible: closed

   .. literalinclude:: sample_rating_team.txt
