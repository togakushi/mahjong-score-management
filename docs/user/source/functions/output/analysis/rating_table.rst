.. _deliverables-rating_table:

レーティング表
==============

記録された成績データを集計し、レーティングを計算する。

:コマンドタイプ: `function-analysis`
:必須オプション: :analysis:`レート` or :analysis:`レーティング`
:ターゲット指定: 任意
:個別オプション: `あり`_


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
     - | ターゲットの指定。
       | 指定プレイヤー/チームだけでレーティング表を生成する。
   * - 集計範囲指定
     - `date-specification` を参照。
   * - その他のオプション
     - `共通オプション <common-options>` を参照。
   * .. _`あり`:

     - 個別オプション
     - .. analysis:: トップ, top
          :category: レーティング個別オプション

     - 指定した順位まで出力。

       :デフォルト: 3
       :指定例: トップ10

       デフォルト値の変更は `analysis セクション <results_management>` の :sub_commands_section:`ranked` で行う。
   * - その他
     - :summary:`グラフ`
     - `deliverables-rating_graph` に切り替える。


項目説明
--------

.. glossary::

   レート : 用語(レーティング項目)
      獲得順位から計算したレーティング。初期値は1500。

   順位偏差 : 用語(レーティング項目)
      集計集団の中の平均順位の偏差。

   得点偏差 : 用語(レーティング項目)
      集計集団の中の平均素点（ゲーム終了時点の持ち点）の偏差。


出力サンプル
------------

.. literalinclude:: ../sample/rating_team.txt
   :caption: チームレーティング
