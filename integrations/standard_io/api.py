"""integrations/standard_io/api.py
"""

import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from integrations.base.interface import APIInterface
from libs.types import StyleOptions
from libs.utils import formatter

if TYPE_CHECKING:
    from integrations.base.interface import MessageParserProtocol


class AdapterAPI(APIInterface):
    """インターフェースAPI操作クラス"""

    def _text_formatter(self, text: str, style: StyleOptions) -> str:
        """テキスト整形

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

    def post(self, m: "MessageParserProtocol"):
        """メッセージ出力

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
                    disp = (
                        formatter.df_rename(x, options)
                        .to_markdown(
                            index=options.show_index,
                            tablefmt="simple_outline",
                            floatfmt=formatter.floatfmt_adjust(x, index=options.show_index),
                            colalign=formatter.column_alignment(x, index=options.show_index),
                        )
                        .replace(" nan ", "-----")
                    )
                    if options.title == "座席データ":
                        disp = disp.replace("0.00", "-.--")
                    print(disp)
                case x if isinstance(x, Path):
                    print(f"{options.title}: {x.absolute()}")
                case _:
                    pass

            print("")
