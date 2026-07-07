.. index::
   pair: メイン設定; alias section
   :name: alias-section

aliasセクション
===============

スラッシュコマンド使用時のサブコマンドの別名を定義。

カンマ区切りで複数ワードの設定が可能。

.. list-table::
   :width: 100%
   :widths: 15 25 15 45
   :header-rows: 1

   * - キー
     - 内容
     - デフォルトエイリアス
     - 備考
   * - .. alias_section:: summary
     - `function-summary` の実行
     - 集計
     -
   * - .. alias_section:: analysis
     - `function-analysis` の実行
     - 分析
     -
   * - .. alias_section:: download
     - データベースのダウンロード
     - ダウンロード
     -
   * - .. alias_section:: member
     - メンバーリストを表示
     - | userlist
       | member_list
     -
   * - .. alias_section:: add
     - メンバーを追加
     -
     - メンバー新規登録、別名登録
   * - .. alias_section:: del
     - メンバーを削除
     -
     - メンバー削除、別名削除
   * - .. alias_section:: team_create
     - 新規チーム作成
     -
     -
   * - .. alias_section:: team_del
     - チームを削除
     -
     - チームに所属していたメンバーは未所属になる
   * - .. alias_section:: team_add
     - チームにメンバーを所属
     -
     - - 複数チームに所属できない
       - `ゲストメンバー` はチームに所属できない
   * - .. alias_section:: team_remove
     - チームからメンバーを削除
     -
     - チーム所属から外れたメンバーは未所属になる
   * - .. alias_section:: team_list
     - チーム一覧と所属メンバーの表示
     -
     -
   * - .. alias_section:: team_clear
     - すべてのチーム情報を削除
     -
     - すべてのチーム情報を削除し、全員未所属に戻す
..
