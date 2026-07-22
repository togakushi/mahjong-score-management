# ドキュメント置き場

## ユーザーマニュアル
https://togakushi.github.io/mahjong-score-management/manual/

## 開発資料 (APIリファレンス)
https://togakushi.github.io/mahjong-score-management/api/


# ドキュメント生成

```
$ cd docs/manual/
$ $ uv run sphinx-build -M html source build --conf-dir .
```

```
$ make -f tests/Makefile docs-user
```
