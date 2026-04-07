クイックスタート
================

コマンドやキーワードをお好みのワードに変えるだけで馴染みやすくなるよ！

.. code-block:: ini
   :caption: メイン設定

   [mahjong]
   # お好みのルールセット
   # point = 250
   # return = 300
   # rank_point = 30, 10, -10, 30
   # draw_split = False
   keywords = お好みの成績記録キーワード

   [setting]
   font_file = ipaexg.ttf

   [results]
   commandword = お好みの成績サマリ呼び出しワード
   guest_skip = False

   [graph]
   commandword = お好みのグラフ呼び出しワード
   guest_skip = False

   [ranking]
   commandword = お好みのランキング呼び出しワード
   aggregation_range = 今月
   guest_skip = False
   ranked = 10

   [report]
   commandword = お好みのレポート呼び出しワード
   aggregation_range = 今年
   guest_skip = False

   [help]
   commandword = お好みのヘルプ呼び出しワード

   [slack]
   slash_command = /設定したスラッシュコマンド
   comparison_word = お好みの突合呼び出しワード
   comparison_alias = お好みの突合スラッシュコマンド名
   search_channel = #成績記録をしているチャンネル名


設定ポイント
------------

- 成績登録ワードを覚えやすいものに変える
- 機能呼び出しキーワードを馴染みのある単語にする
- グラフで使用するフォントを指定する
- 集計期間を省略したときのデフォルト期間を決める

  - ``aggregation_range`` で設定
  - 省略時は **当日**

- ゲストなしをデフォルトの集計オプションにする

  - ``guest_skip`` を ``False`` に設定
  - ゲーム結果はすべて集計されるが、メンバー登録されていないプレイヤーは結果表示から削除される

- ランキングで表示される順位を拡張する

  - ``ranked`` で設定
