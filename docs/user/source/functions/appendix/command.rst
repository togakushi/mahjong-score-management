スラッシュコマンドの使い方
==========================

結果はアプリからDMで通知される。

.. note:: ``/commandname`` は `slack-section` 、 `discord-section`  の ``slash_command`` で定義したもの。


成績管理
--------

.. _slash_commands-results:
.. index::
   pair: slash commands; results

results
+++++++

.. program:: サマリ生成

:概要: 成績を表示
:書式: ``/commandname results [対象メンバー] [検索範囲] [戦績] [詳細] [対戦] [チーム]``
:引数: - 専用オプション

         - :option:`戦績` ：個人成績出力時、検索範囲未指定時でも戦績の結果を出力
         - :option:`詳細` ：戦績に追加で4人分の戦績を出力
         - :option:`対戦` ：対戦結果の表示

           - 対象メンバーを2名以上指定した場合、直接対戦結果を表示

         - 共通オプション

           - `common-argument`

:デフォルトエイリアス: 成績
:補足説明: | 登録名の指定を省略した場合は、検索範囲内の成績サマリの出力。
           | 登録名を指定すると、対象メンバーの個人成績（2ゲスト戦含む）を出力。


.. _slash_commands-ranking:
.. index::
   pair: slash commands; ranking

ranking
+++++++

.. program:: ランキング生成

:概要: 各成績をランキング形式で表示
:書式: ``/commandname ranking [検索範囲] [トップNNN]``
:引数: - 専用オプション

         - :option:`トップ\<NNN>` ：上位NNN位まで表示する（省略時は「3」）

       - 共通オプション

         - `common-argument`

:デフォルトエイリアス: ランキング
:補足説明:


.. _slash_commands-graph:
.. index::
   pair: slash commands; graph

graph
+++++

.. program:: グラフ生成

:概要: ポイント推移グラフを表示
:書式: ``/commandname graph [対象メンバー] [検索範囲]``
:引数: - 専用オプション

         - :option:`順位` ：順位変動グラフに切り替え
         - 集約： :option:`日次` / :option:`月次` / :option:`年次` / :option:`全体`
         - 対象メンバー：省略時は検索範囲に含まれるメンバー全員

       - 共通オプション

         - `common-argument`

:デフォルトエイリアス: グラフ
:補足説明: | 対象メンバーの指定を省略した場合は、検索範囲内で見つかった全メンバーを対象にグラフを生成する。
           | 複数のメンバーが指定された場合、指定されたメンバーのみを対象にグラフを生成する。
           | 単独でメンバーが指定された場合、個人成績(獲得順位、平均順位推移)グラフを追加で生成する。


.. _slash_commands-report:
.. index::
   pair: slash commands; report

report
++++++

:概要: レポートを表示
:書式: ``/commandname report [専用オプション]``
:引数: - 専用オプション

         - 指定なし：成績上位5名（月間）
         - 統計：ゲーム統計（月間）
         - 個人 / 個人成績：個人成績一覧
         - 対戦 / 2名以上のプレイヤー名：対局対戦マトリックス表
         - プレイヤー名：指定プレイヤーの成績レポート(PDF)

       - 共通オプション

         - `common-argument`

:デフォルトエイリアス: レポート
:補足説明:


データベース関連
----------------

.. _slash_commands-check:
.. index::
   pair: slash commands; check

check
+++++

:概要: データベースの突合
:書式: ``/commandname check``
:引数: なし
:デフォルトエイリアス:
:補足説明:


.. _slash_commands-download:
.. index::
   pair: slash commands; download

download
++++++++

:概要: データベースのダウンロード
:書式: ``/commandname download``
:引数: なし
:デフォルトエイリアス: ダウンロード
:補足説明:


メンバー管理
------------

.. _slash_commands-member:
.. index::
   pair: slash commands; member
   pair: slash commands; userlist

member / userlist
+++++++++++++++++

:概要: 登録されているメンバーを表示
:書式: ``/commandname member``
:引数: なし
:デフォルトエイリアス: - userlist
                       - member_list
:補足説明:


.. _slash_commands-member-add-del:
.. index::
   pair: slash commands; add
   pair: slash commands; del

add / del
+++++++++

:概要: 成績管理対象のメンバーを追加、削除
:書式: | ``/commandname add <登録名> [別名]``
       | ``/commandname del <登録名> [別名]``
:引数: - 登録名：サマリや成績管理で表示される名前
       - 別名：登録名に紐付いている別名
:補足説明: | ``/commandname add <登録名>`` でメンバーの新規追加
           | ``/commandname add <登録名> <別名>`` で別名のニックネームを追加
           | ``/commandname del <登録名>`` でメンバーを削除(ゲスト扱い)
           | ``/commandname del <登録名> <別名>`` でニックネームを削除

.. caution:: メンバー登録時の注意事項

   - 最大登録人数は255人
   - 登録できる名前は8文字以内
   - ニックネームは16個まで
   - 半角数字は登録時に全角へ置換される
   - 一部の記号は使用できない


チーム管理
----------

.. _slash_commands-team_create:
.. index::
   pair: slash commands; team_create

team_create
+++++++++++

:概要: チームの新規登録
:書式: ``/commandname team_create <登録チーム名>``
:引数: - 登録チーム名：登録されるチーム名
:デフォルトエイリアス:
:補足説明:


.. _slash_commands-team_del:
.. index::
   pair: slash commands; team_del

team_del
++++++++

:概要: チームの削除
:書式: ``/commandname team_del <チーム名>``
:引数: - チーム名：削除されるチーム名
:デフォルトエイリアス:
:補足説明: 所属していたメンバーは自動的に未所属に更新される


.. _slash_commands-team_add:
.. index::
   pair: slash commands; team_add

team_add
++++++++

:概要: チームにメンバーを所属させる
:書式: | ``/commandname team_add <チーム名>``
       | ``/commandname team_add <チーム名> <メンバー名>``
:引数: - チーム名：所属させるチーム名
       - メンバー名：所属するメンバー名
:デフォルトエイリアス:
:補足説明: - メンバーの指定がない場合、 ``team_create`` と同じ動作をする
           - 別チームに所属している場合、新しい情報で更新される


.. _slash_commands-team_remove:
.. index::
   pair: slash commands; team_remove

team_remove
+++++++++++

:概要: メンバーを未所属にする
:書式: ``/commandname team_remove <メンバー名>``
:引数: - メンバー名：未所属にするメンバー名
:デフォルトエイリアス:
:補足説明:


.. _slash_commands-team_list:
.. index::
   pair: slash commands; team_list

team_list
+++++++++
:概要: チーム名と所属メンバーを表示する
:書式: ``/commandname team_list``
:引数: なし
:デフォルトエイリアス:
:補足説明:


.. _slash_commands-team_clear:
.. index::
   pair: slash commands; team_clear

team_clear
++++++++++

:概要: チーム情報をすべて削除する
:書式: ``/commandname team_clear``
:引数: なし
:デフォルトエイリアス:
:補足説明: - すべてのチームは削除される
           - すべてのメンバーは未所属になる
