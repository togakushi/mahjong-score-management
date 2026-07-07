テストデータ生成
================

ツール起動
----------

- 基本設定
- 空DB生成


データ準備
----------

.. code-block:: shell
   :caption: サンプルメンバーインポート

   $ uv run dbtools.py --import ./tests/test_data/saki

- 1チーム5人編成
- 16チーム


データ生成
----------

.. code-block:: shell
   :caption: シミュレーションデータ投入

   $ uv run dbtools.py --gen-test-data

- 16チーム総当たり戦

  - 2275戦/チーム
  - 455戦/人
