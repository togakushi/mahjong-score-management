ランキング生成
==============

記録された成績データを集計し、ランキングを作成する。

.. program:: ランキング生成

構文
----

:チャンネル内呼び出し: <呼び出しキーワード> [オプション]
:スラッシュコマンド: /commandname ranking [オプション]

.. note:: ``/commandname`` は `slack-section` 、 `discord-section`  の ``slash_command`` で定義したもの。


オプション
----------

.. option:: トップ<NNN>

   上位NNN位まで出力。

.. option:: レート, レーティング, rating

   レーティングを表示。


共通オプション
--------------

- `common-argument`


項目説明
--------

ランキング
++++++++++

通算ポイント
   ウマ、オカを足して最終得点を確定させて算出したポイントの合計。

平均ポイント
   通算ポイントをゲーム数で割ったもの。

平均収支
   各ゲームの「素点-配給原点」の平均点を出したもの。

トップ率
   トップ（1位）を取った回数/ゲーム数。

連対率
   連対（1位と2位）を取った回数/ゲーム数。
   順位点がプラスの着順を取ってる率。

ラス回避率
   4着以外（1位と2と3位）を取った回数/ゲーム数。

トビ率
   素点がマイナスになった率。
   トビにくいプレイヤーが上位。

平均順位
   獲得着順をゲーム数で割った平均値。
   2.5が基準。小さいほうが優秀。


レーティング
++++++++++++

レート
   獲得順位から計算したレーティング。初期値は1500。

順位偏差
   集計集団の中の平均順位の偏差。

得点偏差
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
