"""
integrations/standard_io/api.py
"""

import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from integrations.base.interface import APIInterface
from libs.types import StyleOptions
from libs.utils import formatter

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class AdapterAPI(APIInterface):
    """インターフェースAPI操作クラス"""

    def _text_formatter(self, text: str, style: StyleOptions) -> str:
        """
        テキスト整形

        Args:
            text (str): 対象テキスト
            style (StyleOptions): 修飾オプション

        Returns:
            str: 整形済みテキスト

        """
        ret: str = ""
        for line in text.splitlines():
            line = line.replace("<@>", "")
            if not style.keep_indent:
                line = textwrap.dedent(line)
            if line or style.keep_blank:
                ret += textwrap.indent(f"{line}\n", "\t" * style.indent)
        return ret.rstrip()

    def post(self, m: "MessageParserProtocol") -> None:
        """
        メッセージ出力

        Args:
            m (MessageParserProtocol): メッセージデータ

        """
        # 見出し
        if m.post.headline:
            header_data, header_option = m.post.headline
            if isinstance(header_data, str):
                print("=" * 80)
                if header_option.title:
                    print(f"【{header_option.title}】")
                if isinstance(header_data, str):
                    print(textwrap.dedent(header_data).rstrip())
                    print("=" * 80)

        # 本文
        for data, options in m.post.message:
            if options.key_title and options.title:
                print(options.print_title)

            match data:
                case x if isinstance(x, str):
                    print(self._text_formatter(x, options))
                case x if isinstance(x, pd.DataFrame):
                    options.rename_type = StyleOptions.RenameType.NORMAL
                    match options.data_kind:
                        case StyleOptions.DataKind.POINTS_TOTAL:
                            x["total_point"] = x.apply(lambda df: f"{df['total_point']:+.1f}pt".replace("-", "▲"), axis=1)
                            x["avg_point"] = x.apply(lambda df: f"{df['avg_point']:+.1f}pt".replace("-", "▲"), axis=1)
                        case StyleOptions.DataKind.POINTS_DIFF:
                            x["total_point"] = x.apply(lambda df: f"{df['total_point']:+.1f}pt".replace("-", "▲"), axis=1)
                            x["diff_from_above"] = x["diff_from_above"].map(lambda v: f"{v:.1f}pt" if pd.notna(v) else "------")
                            x["diff_from_top"] = x["diff_from_top"].map(lambda v: f"{v:.1f}pt" if pd.notna(v) else "------")
                        case _:
                            pass
                    disp = formatter.df_rename(x, options).to_markdown(
                        index=options.show_index,
                        tablefmt="simple_outline",
                        floatfmt=formatter.floatfmt_adjust(x, index=options.show_index),
                        colalign=formatter.column_alignment(x, index=options.show_index),
                    )
                    print(disp)
                case x if isinstance(x, Path):
                    print(f"{options.title}: {x.absolute()}")
                case _:
                    pass

            print("")
