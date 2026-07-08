コマンド専用オプション
======================

コマンドの動作を変更するために指定する専用のオプション。


.. _option-summary:

集計コマンドオプション
----------------------

.. list-table::
   :width: 100%
   :widths: 20 30 40
   :header-rows: 1

   * - キーワード
     - 内容
     - 備考
   * - .. summary:: グラフ
     - ポイント集計、順位集計の表を折れ線グラフの表示に切り替える
     - .. 備考
   * - .. summary:: 順位
     - 順位変動、月間生成上位の表示に切り替える
     - .. 備考
   * - .. summary:: 比較, 差分, 点差
     - 通算ポイント集計表を差分形式に切り替える
     - .. 備考
   * - .. summary:: 対戦, 対戦結果
     - 対戦相手とのゲーム結果を表示する
     - `ターゲット` の指定状況で動作が変化する

       :任意: `deliverables-direct_match` の表示
       :単独: `deliverables-results_details` にゲーム同卓者との対戦結果を追加表示
..
.. seealso:: `オプション組み合わせ表 - 集計コマンド <summary_option_combination>`


.. _option-analysis:

分析コマンドオプション
----------------------

.. list-table::
   :width: 100%
   :widths: 20 30 40
   :header-rows: 1

   * - キーワード
     - 内容
     - 備考
   * - .. analysis:: グラフ
     - グラフ表記に切り替える
     - .. 備考
   * - .. analysis:: レポート
     - レポートを生成する
     - `ターゲット` の指定状況で動作が変化する

       :任意: `deliverables-game_statistics` の表示
       :単独: `deliverables-results_report` の生成

   * - .. analysis:: レート, レーティング
     - レーティングを集計
     - .. 備考
   * - .. analysis:: 対戦, 対戦結果
     - `deliverables-matchup_matrix` の表示
     - .. 備考
   * - .. analysis:: 統計
     - 統計情報の表示（比較用）
     - 他のオプションの指定状態に依存する
   * - .. analysis:: 素点
     - ゲーム終了時点の素点情報を基にした成績の分析を行う
     - .. 備考
..
.. seealso:: `オプション組み合わせ表 - 分析コマンド <analysis_option_combination>`
