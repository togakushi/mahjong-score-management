.. _deliverables-results_analysis:

成績分析
========

指定回数区切りの集計をグラフで出力する。

:コマンドタイプ: `function-analysis`
:必須オプション: :analysis:`グラフ`
:ターゲット指定: 単独
:個別オプション: `あり <option-analysis>`



オプション
----------

.. flat-table::
   :header-rows: 1
   :width: 100%
   :widths: 10 20 70

   * - 分類
     - 項目
     - 内容
   * - :rspan:`2` 共通オプション
     - | プレイヤー名
       | チーム名
     - | `ターゲット` の指定（単独）。
       | 指定プレイヤー/チームの成績分析を生成する。
   * - 集計範囲指定
     - `date-specification` を参照。
   * - その他のオプション
     - `common-options` を参照。
   * - :rspan:`3` 個別オプション
     - .. analysis:: 区切り, 区切, 期間, 区間
     - 集計区間の変更

       :デフォルト: 80
       :指定例: 区切200

       デフォルト値の変更は `analysisセクション <results_management>` の :sub_commands_section:`interval` で行う。


項目説明
--------

ポイント推移（折れ線グラフ）
   :区間ポイント: 集計区間内のポイント合計値
   :区間平均: 集計区間内のポイント平均値
   :通算ポイント: 集計区間までのポイント合計値

獲得順位（棒グラフ）
   集計区間内の獲得順位率と回数

素点分布（箱ひげ図）
   :平均値: 集計区間の素点平均値
   :最小値: 集計区間内の素点最小値
   :第一四分位数: 集計区間内のデータで小さい方から25%の位置にある素点（下位データの中央値）
   :中央値: 集計区間内のデータで50%の位置にある素点（第二四分位数）
   :第三四分位数: 集計区間内のデータで小さい方から75%の位置にある素点（上位データの中央値）
   :最大値: 集計区間内の素点最大値


出力サンプル
------------

.. admonition:: 成績分析

   .. compound::

      .. image:: ../sample/separator_graph_ggplot.png
         :scale: 30%
         :alt: 出力サンプル(ggplot)

      .. image:: ../sample/separator_graph_dark.png
         :scale: 30%
         :alt: 出力サンプル(dark_background)
