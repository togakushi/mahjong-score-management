# mahjong-score-management

## 概要

麻雀のスコアを記録、集計するツール。

### セットアップ方法

* [Slack](https://togakushi.github.io/mahjong-score-management/manual/admins/setting/for_slack/index.html)
* [Discord](https://togakushi.github.io/mahjong-score-management/manual/admins/setting/for_discord/index.html)

## 主な機能

### スコア記録（ [詳細](https://togakushi.github.io/mahjong-score-management/manual/users/record/score.html) ）

以下のフォーマットに一致した投稿をデータベースに取り込む。

```
<成績記録キーワード>
東家プレイヤー名 東家素点
南家プレイヤー名 南家素点
西家プレイヤー名 西家素点
北家プレイヤー名 北家素点
```

> [!TIP]
> 入力した素点から順位を算出し、定義されている順位点を加算してデータベースに取り込まれる。

### メンバー管理

成績管理をするプレイヤーを登録し、スコアを蓄積する。

### 成績集計

* 成績サマリ出力（ [詳細](https://togakushi.github.io/mahjong-score-management/manual/users/functions/summary/results_table_all.html) ）
  * 記録されているスコアを集計し、一覧で出力する。

* グラフ生成（ [詳細](https://togakushi.github.io/mahjong-score-management/manual/users/functions/summary/point_transition.html) ）
  * 記録されているスコアを集計し、グラフで出力する。

* 成績詳細（ [詳細](https://togakushi.github.io/mahjong-score-management/manual/users/functions/summary/results_details.html)）
  * トップ率など詳細生成を集計する。

### 成績分析

* ランキング出力（ [詳細](https://togakushi.github.io/mahjong-score-management/manual/users/functions/analysis/ranking.html) ）
  * 記録されているスコアを集計し、ランキング形式で出力する。
