.. index::
   single: メイン設定; 装飾オプション

装飾設定
========

| 使用しない(常に非表示)とする場合はセクションごと省略してよい。
| デフォルト値は持たないため、設定時はすべてのキーの設定が必要になる。


.. _degree-section:

degreeセクション
----------------

| プレイしたゲーム数に対して表示される称号。
| 表示/非表示の設定は :ref:`integrations-common` で行う。

.. list-table::
   :width: 100%
   :widths: 10 20 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 備考
   * - :index:`badge <pair: degree section; badge>`
     - 追加される文字列
     - | 文字列
       | (カンマ区切り)
     - ``counter`` の数と合わせる
   * - :index:`counter <pair: degree section; counter>`
     - 称号が変化するゲーム数
     - | 数値(int)
       | (カンマ区切り)
     - ``badge`` の数と合わせる


.. _status-section:

statusセクション
----------------

| 勝率に対して付く調子バッジ。
| 表示/非表示の設定は :ref:`integrations-common` で行う。

.. list-table::
   :width: 100%
   :widths: 10 20 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 備考
   * - :index:`badge <pair: status section; badge>`
     - 追加される文字列
     - | 文字列
       | (カンマ区切り)
     - 休み、絶不調、不調、普通、好調、絶好調の順に6段階すべて指定
   * - :index:`step <pair: status section; step>`
     - 称号が変化するゲーム数
     - 数値(float)
     - 普通を基準(勝率50%)として、上下する刻み幅


.. _grade-section:

gradeセクション
---------------

| 段位設定。
| 表示/非表示の設定は :ref:`integrations-common` で行う。

.. list-table::
   :width: 100%
   :widths: 10 20 10 40
   :header-rows: 1

   * - キー
     - 内容
     - 値
     - 備考
   * - :index:`table_name <pair: grade section; table_name>`
     - 使用する昇段計算テーブルの名前
     - 文字列(備考参照)
     - :mahjongsoul / 雀魂: 雀魂風表記
       :tenho / 天鳳: 天鳳風表記
       :その他(JSONファイル名): オリジナル定義ファイルを使用( :ref:`gradetable` 参照)


.. index::
   single: メイン設定; メッセージカスタマイズオプション

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
   * - :index:`invalid_argument <pair: custom_message section; invalid_argument>`
     - オプション解析に失敗した場合
     -
   * - :index:`invalid_score <pair: custom_message section; invalid_score>`
     - 持ち点合計と配給原点合計に差分がある場合
     -
   * - :index:`no_hits <pair: custom_message section; no_hits>`
     - 検索指定範囲にゲーム結果が見つからない場合
     -
   * - :index:`no_target <pair: custom_message section; no_target>`
     - 集計対象メンバーが存在しない場合
     -
   * - :index:`restricted_channel <pair: custom_message section; restricted_channel>`
     - 制限チャンネルでデータ更新をしようとした場合
     -
   * - :index:`inside_thread <pair: custom_message section; inside_thread>`
     - ``thread_report`` が ``False`` の場合にスレッド内で点数登録をしようとした場合
     -
   * - :index:`same_player <pair: custom_message section; same_player>`
     - スコアデータに同名のプレイヤーが存在している場合
     -
   * - :index:`not_implemented <pair: custom_message section; not_implemented>`
     - 未実装の機能にアクセスしたときに表示するメッセージ
     -
   * - :index:`access_denied <pair: custom_message section; access_denied>`
     - 制限された機能にアクセスしたときに表示するメッセージ
     -
   * - :index:`rule_mismatch <pair: custom_message section; rule_mismatch>`
     - 集計モードと指定ルールセットのモードに食い違いが発生している場合
     -


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
