.. _function-report:

レポート生成
============

記録された成績データを集計し、一覧にまとめる。


構文
----

:チャンネル内呼び出し: <呼び出しキーワード> [オプション]
:スラッシュコマンド: /commandname report [オプション]

.. note::
   ``/commandname`` は以下で定義する

   - `slack-section` の :integrations_section:`slash_command <slack section; slash_command>`
   - `discord-section` の :integrations_section:`slash_command <discord section; slash_command>`


オプション
----------

基本オプション
++++++++++++++

.. report:: メンバー名, チーム名
   :category: 基本オプション

   指定メンバー / チームの成績レポートを生成する。


個別オプション
++++++++++++++

   .. list-table::
      :width: 100%
      :widths: 15 20 50
      :header-rows: 1

      * - キーワード
        - 出力内容
        - 備考
      * - 指定なし
        - 個人/チーム成績一覧
        - reportセクションの ``individual`` で変化
      * - .. report:: 順位
             :category: 個別オプション

        - 成績上位者
        - 上位5名
      * - .. report:: 統計
             :category: 個別オプション
        - ゲーム統計
        - 検索範囲に記録されているすべての結果
      * - .. report:: 対戦
             :category: 個別オプション

        - 対局対戦マトリックス表
        - テキスト or CSV出力
      * - 2名以上のプレイヤー名
        - 対局対戦マトリックス表
        - 指定プレイヤーに絞って出力


共通オプション
++++++++++++++

- `common-options`


レポート内容
------------

.. describe:: 成績上位者

   月間の通算ポイントが多い順に5名を表示。

.. describe:: 統計

   | 検索範囲のゲーム結果についてのゲーム傾向を月単位で集計。
   | （ゲスト関連のオプションは無視される）

.. describe:: 個人成績 / チーム成績

   個人/チーム成績の一覧表を表示。

.. describe:: 成績レポート

   対象メンバーの成績集計をPDFで出力。

   - 全期間
   - 月単位
   - 年単位
   - 区間

     - 100戦以上で80戦区切り
     - 240戦以上で200戦区切り
     - 500戦以上で400戦区切り

.. describe:: 対局対戦マトリックス表

   | 対局相手との勝敗をカウント。
   | 相手より順位が上なら勝ち、下なら負けにカウントされる。


出力サンプル
------------

.. admonition:: チーム成績一覧
   :collapsible: closed

   .. image:: sample_team_stats_list.png
      :scale: 30%
      :alt: チーム成績一覧

.. admonition:: 対局対戦マトリックス表
   :collapsible: closed

   .. literalinclude:: sample_matrix.txt
      :caption: 対局対戦マトリックス表
