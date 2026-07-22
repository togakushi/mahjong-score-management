.. index::
   single: メイン設定; メッセージカスタマイズ設定

メッセージカスタマイズ設定
==========================

.. _custom_message-section:

custom_messageセクション
------------------------

| 使用シーン別のプレフィックスが付いたキーに表示メッセージを定義。
| プレフィックス以降の文字列は任意。

セクション内でユニークになるように定義すること（ランダムに選択される）。

.. list-table::
   :width: 100%
   :widths: 10 50 30
   :header-rows: 1

   * - プレフィックス
     - 使用シーン
     - 備考
   * - .. custom_message_section:: invalid_argument
     - オプション解析に失敗した場合
     -
   * - .. custom_message_section:: invalid_score
     - 持ち点合計と配給原点合計に差分がある場合
     -
   * - .. custom_message_section:: no_hits
     - 検索指定範囲にゲーム結果が見つからない場合
     -
   * - .. custom_message_section:: no_target
     - 集計対象メンバーが存在しない場合
     -
   * - .. custom_message_section:: restricted_channel
     - 制限チャンネルでデータ更新をしようとした場合
     -
   * - .. custom_message_section:: inside_thread
     - `thread_report` が ``False`` の場合にスレッド内で点数登録をしようとした場合
     -
   * - .. custom_message_section:: same_player
     - スコアデータに同名のプレイヤーが存在している場合
     -
   * - .. custom_message_section:: not_implemented
     - 未実装の機能にアクセスしたときに表示するメッセージ
     -
   * - .. custom_message_section:: access_denied
     - 制限された機能にアクセスしたときに表示するメッセージ
     -
   * - .. custom_message_section:: rule_mismatch
     - 集計モードと指定 `ルールセット` のモードに食い違いが発生している場合
     -

..


置き換え文字列
++++++++++++++

| メッセージ内の特定文字列は以下のように置き換えられる。
| 無効な置き換え文字列が含まれている場合、 ``{user_id}`` 以外の文字列はそのまま表示される（置き換えは行われない）。

.. list-table::
   :width: 100%
   :widths: 10 50 30
   :header-rows: 1

   * - 置き換え文字列
     - 置き換え後の文字
     - 備考
   * - {user_id}
     - コマンドを投入したユーザのslack id
     - メンションは ``<@{user_id}>``
   * - {rpoint_diff}
     - 点数差分の絶対値
     - 配給原点 * 4 - 入力点数合計
   * - {rpoint_sum}
     - 素点合計
     - 入力された点数の合計値
   * - {keyword}
     - 成績記録キーワード
     -
   * - {start}
     - 指定した検索開始日時
     - ``YYYY/MM/DD hh:mm``
   * - {end}
     - 指定した検索終了日時
     - ``YYYY/MM/DD hh:mm``
