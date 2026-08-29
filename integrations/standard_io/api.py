"""
integrations/standard_io/api.py
"""

import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from integrations.base.interface import APIInterface
from libs.functions import adjusting
from libs.types import StyleOptions
from libs.utils import dictutil

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
                    x = adjusting.add_units(x)  # 単位付与/文字列変換
                    if options.show_index and isinstance(x.index.name, str):
                        if new_index := dictutil.rename_dicts([x.index.name], options).get(x.index.name):
                            x.index.name = new_index
                    disp = x.rename(
                        columns=dictutil.rename_dicts(x.columns.to_list(), options),
                    ).to_markdown(
                        tablefmt="simple_outline",
                        index=options.show_index,
                        floatfmt=adjusting.floatfmt(x, index=options.show_index),
                        headersalign=adjusting.column_alignment(x, header=True, index=options.show_index),
                        colalign=adjusting.column_alignment(x, header=False, index=options.show_index),
                    )
                    print(disp)
                case x if isinstance(x, Path):
                    print(f"- {x.absolute()}")
                case _:
                    pass

            print("")
