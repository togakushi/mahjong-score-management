#!/usr/bin/env python3
"""
dbtools.py - DB管理補助ツール

help:
    usage: dbtools.py [-h] ...

    options:
        -h, --help
            show this help message and exit
        -c CONFIG, --config=CONFIG
            設定ファイル(default: config.ini)
        -s SERVICE, --service=SERVICE
            連携先サービス(slack, standard_io, std,web, flask)

    logging options:
        -d, --debug
            デバッグレベル(-d, -dd)
        -v, --verbose
            動作ログ出力レベル(-v, -vv, -vvv)
        --moderate
            ログレベルがエラー以下のもを非表示
        --notime
            ログフォーマットから日時を削除

    Required options(amutually exclusive):
        --compar
            データ突合
        --unification=UNIFICATION
            ファイルの内容に従って記録済みのメンバー名を修正する(default: rename.ini)
        --recalculation [RULE_VERSION ...]
            ポイント再計算(引数なし=全ルール, 引数あり=指定ルールのみ)
        --export=PREFIX
            メンバー設定情報をエクスポート(default prefix: export)
        --import=PREFIX
            メンバー設定情報をインポート(default prefix: export)
        --vacuum
            database vacuum
        --gen-test-data=count
            テスト用サンプルデータ生成(count=生成回数, default: 1)
"""

import libs.global_value as g
from libs.bootstrap import configuration
from libs.functions.tools import comparison, gen_test_data, member, recalculation, unification, vacuum

if __name__ == "__main__":
    configuration.initialize()

    if g.args.compar:
        comparison.main()
    if g.args.recalculation or g.args.recalculation is not None:
        recalculation.main()
    if g.args.unification:
        unification.main()
    if g.args.export_data:
        member.export_data()
    if g.args.import_data:
        member.import_data()
    if g.args.vacuum:
        vacuum.main()
    if g.args.gen_test_data:
        gen_test_data.main(g.args.gen_test_data)
