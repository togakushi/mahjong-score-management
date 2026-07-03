スラッシュコマンドの使い方
==========================

結果はアプリからDMで通知される。

.. note::
   ``/commandname`` は以下で定義する

   - `slack-section` の :integrations_section:`slash_command <slack section; slash_command>`
   - `discord-section` の :integrations_section:`slash_command <discord section; slash_command>`


成績管理
--------

.. index::
   pair: slash commands; summary
   :name: slash_commands-summary

summary
+++++++

:概要: `function-summary` を実行
:書式: ``/commandname summary`` [`ターゲット`] [`オプション`]
:デフォルトエイリアス: 集計
:補足説明:


.. index::
   pair: slash commands; analysis
   :name: slash_commands-analysis

analysis
++++++++

:概要: `function-analysis` を実行
:書式: ``/commandname analysis`` [`ターゲット`] [`オプション`]
:デフォルトエイリアス: 分析
:補足説明:


データベース関連
----------------

.. index::
   pair: slash commands; check
   :name: slash_commands-check

check
+++++

:概要: データベースの突合
:書式: ``/commandname check``
:引数: なし
:デフォルトエイリアス:
:補足説明:


.. index::
   pair: slash commands; download
   :name: slash_commands-download:

download
++++++++

:概要: データベースのダウンロード
:書式: ``/commandname download``
:引数: なし
:デフォルトエイリアス: ダウンロード
:補足説明:


メンバー管理
------------

.. seealso:: `member-management`

.. index::
   pair: slash commands; member
   :name: slash_commands-member

member
++++++

:概要: 登録されているメンバーを表示
:書式: ``/commandname member``
:引数: なし
:デフォルトエイリアス: - userlist
                       - member_list
:補足説明:


.. index::
   pair: slash commands; add
   pair: slash commands; del
   :name: slash_commands-member-add-del

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

.. seealso:: `team-management`

.. index::
   pair: slash commands; team_create
   :name: slash_commands-team_create

team_create
+++++++++++

:概要: チームの新規登録
:書式: ``/commandname team_create <登録チーム名>``
:引数: - 登録チーム名：登録されるチーム名
:デフォルトエイリアス:
:補足説明:


.. index::
   pair: slash commands; team_del
   :name: slash_commands-team_del

team_del
++++++++

:概要: チームの削除
:書式: ``/commandname team_del <チーム名>``
:引数: - チーム名：削除されるチーム名
:デフォルトエイリアス:
:補足説明: 所属していたメンバーは自動的に未所属に更新される


.. index::
   pair: slash commands; team_add
   :name: slash_commands-team_add

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


.. index::
   pair: slash commands; team_remove
   :name: lash_commands-team_remove

team_remove
+++++++++++

:概要: メンバーを未所属にする
:書式: ``/commandname team_remove <メンバー名>``
:引数: - メンバー名：未所属にするメンバー名
:デフォルトエイリアス:
:補足説明:


.. index::
   pair: slash commands; team_list
   :name: slash_commands-team_list

team_list
+++++++++

:概要: チーム名と所属メンバーを表示する
:書式: ``/commandname team_list``
:引数: なし
:デフォルトエイリアス:
:補足説明:


.. index::
   pair: slash commands; team_clear
   :name: slash_commands-team_clear

team_clear
++++++++++

:概要: チーム情報をすべて削除する
:書式: ``/commandname team_clear``
:引数: なし
:デフォルトエイリアス:
:補足説明: - すべてのチームは削除される
           - すべてのメンバーは未所属になる
