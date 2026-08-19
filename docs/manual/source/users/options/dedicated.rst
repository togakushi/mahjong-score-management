コマンド専用オプション
======================

コマンドの動作を変更するために指定する専用のオプション。


.. _option-summary:

集計コマンドオプション
----------------------

.. flat-table::
   :width: 100%
   :widths: 10 15 35 40
   :header-rows: 1

   * - 分類
     - キーワード
     - 内容
     - 備考
   * - :rspan:`2` 出力切替
     - .. summary:: グラフ
     - ポイント集計、順位集計の表を折れ線グラフの表示に切り替える
     - `ターゲット` の指定状況で動作が変化する

       :単独: `deliverables-results_graph`
       :任意: `deliverables-point_transition`
       :任意 + 順位: `deliverables-ranking_change`
   * - .. summary:: 順位
     - 順位に関する情報の表示
     - :summary:`グラフ` オプションの有無で出力内容が切り替わる

       :あり: `deliverables-ranking_change`
       :なし: `deliverables-winner`

   * - .. summary:: 比較, 差分, 点差
     - `deliverables-results_table_diff` を表示する
     - `deliverables-results_table_all` から切り替わる
   * - | 出力切替
       | 個別
     - .. summary:: 対戦, 対戦結果
     - 対戦相手とのゲーム結果を表示する
     - `ターゲット` の指定状況で動作が変化する

       :任意: `deliverables-direct_match` の表示
       :単独: `deliverables-results_details` にゲーム同卓者との対戦結果を追加表示
   * - :rspan:`2` 個別
     - .. summary:: 統計
     - `deliverables-results_details` に統計情報を追加表示する
     - 座席データ、 `ベストレコード` 、 `ワーストレコード` 、収支情報の追加表示
   * - .. summary:: 戦績
     - `deliverables-results_details` に戦績データを追加表示する
     - ゲーム単位の素点、順位、獲得ポイントの追加表示
   * - .. summary:: 詳細
     - 戦績データを4人分表示する
     - :summary:`戦績` 同時指定した場合のみ有効
..
.. seealso:: `オプション組み合わせ表 - 集計コマンド <summary_option_combination>`


.. _option-analysis:

分析コマンドオプション
----------------------

.. flat-table::
   :width: 100%
   :widths: 10 15 35 40
   :header-rows: 1

   * - 分類
     - キーワード
     - 内容
     - 備考
   * - :rspan:`6` 出力切替
     - .. analysis:: グラフ
     - グラフ表記に切り替える
     - .. 備考
   * - .. analysis:: レポート
     - `deliverables-results_report` を生成する
     - `ターゲット` が ``単独`` 指定以外の場合は `deliverables-ranking` が表示される
   * - .. analysis:: レート, レーティング
     - レーティングを集計する
     - :analysis:`グラフ` オプションの有無で出力内容が切り替わる

       :あり: `deliverables-rating_graph`
       :なし: `deliverables-rating_table`
   * - .. analysis:: 対戦, 対戦結果
     - `deliverables-matchup_matrix` を表示する
     - .. 備考
   * - .. analysis:: 統計
     - `deliverables-game_statistics` を表示する
     - .. 備考
   * - .. analysis:: 素点
     - ゲーム終了時点の素点情報を基にした成績の分析を行う
     - :analysis:`グラフ` オプションの有無で出力内容が切り替わる

       :あり: `deliverables-score_chart`
       :なし: `deliverables-score_analysis`
   * - .. analysis:: 比較
     - `deliverables-results_list` を表示する
     - .. tip::
          `option-analysis` と共用のため、:summary:`差分` / :summary:`点差` の指定時も `deliverables-results_list` が表示される
   * - :rspan:`1`  個別
     - .. analysis:: ベスト, トップ, 上位, best, top
     - 指定した順位までの出力に制限する

       - `deliverables-ranking`
       - `deliverables-rating_table`

     -
       :指定例: トップ10
       :デフォルト: 3

       デフォルト値の変更は `analysisセクション <results_management>` の :sub_commands_section:`ranked` で行う
   * - .. analysis:: 詳細
     - `deliverables-results_list` に詳細情報を追加表示する
     - 収支情報、 `ベストレコード` 、 `ワーストレコード` の追加表示
..
.. seealso:: `オプション組み合わせ表 - 分析コマンド <analysis_option_combination>`


.. _option-others:

その他のコマンドで使用できるオプション
--------------------------------------

.. flat-table::
   :width: 100%
   :widths: 10 15 35 40
   :header-rows: 1

   * - 分類
     - キーワード
     - 内容
     - 備考
   * - `function-members_list`
     - .. common:: 詳細
     - 詳細表示に切り替える
     - 各メンバーの最終更新日、経過日数、総対戦数を表示する
