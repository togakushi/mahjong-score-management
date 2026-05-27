"""
日付範囲計算とフォーマット変換を検証するテスト。
"""

from typing import Any

import pytest

from libs.utils.timekit import ExtendedDatetime as ExtDt
from tests.utils import param_data


@pytest.mark.parametrize(
    "date, keyword_list, period",
    list(param_data.date_range.values()),
    ids=list(param_data.date_range.keys()),
)
def test_keyword_range(date: str, keyword_list: list[str], period: list[str]) -> None:
    """
    日付範囲キーワードごとの期間算出結果を検証する。

    同一基準日に対する複数キーワードの period が期待値と一致するか確認する。

    """
    for keyword in keyword_list:
        dt = ExtDt(date).range(keyword)

        print(f"{date}, {keyword} -> {dt.period} = {period}")
        assert dt.period == period


@pytest.mark.parametrize(
    "date, option, output",
    list(param_data.format_conv.values()),
    ids=list(param_data.format_conv.keys()),
)
def test_format_conv(date: str, option: list[Any], output: str) -> None:
    """
    日付フォーマット変換結果を検証する。

    書式・区切り指定の組み合わせごとに format の出力を期待値と照合する。

    """
    args: dict[str, Any] = {}
    for x in option:
        if isinstance(x, ExtDt.FMT):
            args.update(fmt=x)
        if isinstance(x, ExtDt.DEM):
            args.update(delimiter=x)

    dt = ExtDt(date)
    assert dt.format(**args) == output
