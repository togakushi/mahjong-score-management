成績管理
========

内容説明
--------

.. toctree::
   :maxdepth: 2
   :includehidden:
   :titlesonly:

   summary/index
   analysis/index


コマンド処理ロジック
--------------------

入力された文字列は以下の順序で評価され、出力される内容が決定される。

#. `コマンド` 部分と `オプション` 部分の分割

   スペース区切りで分割され、最初のブロックがコマンド、残りのブロックはすべてオプションとして扱われる

#. ショートカットの適応

   - ショートカットが設定されていれば、コマンド部分とショートカットを置換する

     .. seealso:: `shortcut-section`

#. コマンド種別の判定

   - `function-summary`
   - `function-analysis`
   - `その他のコマンド <function-others>`

#. ターゲットの判定

   ターゲットの指定方法とコマンド種別の組み合わせで出力内容が決定される

   - 未指定（任意）
   - 単独指定
   - 複数指定

#. オプションの評価

   .. seealso:: `option-logic`
