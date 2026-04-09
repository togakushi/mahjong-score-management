.. index::
   single: ルールセット; 設定ファイル

.. _rule-config:

ルール設定ファイル
==================

成績集計に使用するルールセットを定義する。

ルールセットは以下で定義される。

- メイン設定ファイル内「`mahjong-section`」

  - 1セットのみ定義可能
  - セクションの省略可能

- メイン設定ファイル内「 `setting-section` 」の ``rule_config`` で指定される設定ファイル

  - 複数セットの定義が可能
  - 省略可能

``rule_config`` で指定される設定ファイルではルールセットを区別できるユニークなセクションを設け、そのセクション内にパラメータを定義する。

.. tip::
   ルールセット定義がすべて省略された場合はプリセット（ :manpage:`default_rule.ini` ）が使用される。

----

.. toctree::
   :caption: 設定内容
   :maxdepth: 2

   ruleset
   regulations
