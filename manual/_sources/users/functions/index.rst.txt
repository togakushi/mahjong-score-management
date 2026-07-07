成績管理機能説明
================

.. toctree::
   :caption: 内容説明
   :maxdepth: 2
   :titlesonly:
   :includehidden:

   summary/index
   analysis/index
   help/index

----

.. describe:: コマンドルーティング

   入力されたコマンドは以下の順序で評価され、出力される内容が決定される。

   #. コマンド種別の判定

      - `function-summary`
      - `function-analysis`
      - `function-help`

   #. ターゲットの判定

      - 未指定（任意）
      - 単独指定
      - 複数指定

   #. オプションの評価

      #. 必須オプションの有無
      #. 追加オプションの有無
