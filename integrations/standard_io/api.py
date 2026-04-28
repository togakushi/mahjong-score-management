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
                    match options.data_kind:  # 単位付与/文字列変換
                        case StyleOptions.DataKind.POINTS_TOTAL:
                            if "total_point" in x.columns:
                                x["total_point"] = x["total_point"].map(lambda v: f"{v:+.1f}pt".replace("-", "▲"))
                            if "avg_point" in x.columns:
                                x["avg_point"] = x["avg_point"].map(lambda v: f"{v:+.1f}pt".replace("-", "▲"))
                        case StyleOptions.DataKind.POINTS_DIFF:
                            if "total_point" in x.columns:
                                x["total_point"] = x["total_point"].map(lambda v: f"{v:+.1f}pt".replace("-", "▲"))
                            if "diff_from_above" in x.columns:
                                x["diff_from_above"] = x["diff_from_above"].map(lambda v: f"{v:.1f}pt" if pd.notna(v) else "------")
                            if "diff_from_top" in x.columns:
                                x["diff_from_top"] = x["diff_from_top"].map(lambda v: f"{v:.1f}pt" if pd.notna(v) else "------")
                        case StyleOptions.DataKind.RECORD_DATA:
                            if "rank" in x.columns:
                                x["rank"] = x["rank"].map(lambda v: f"{v:.0f}位")
                            if "rpoint" in x.columns:
                                x["rpoint"] = x["rpoint"].map(lambda v: f"{v:.0f}点".replace("-", "▲"))
                            if "point" in x.columns:
                                x["point"] = x["point"].map(lambda v: f"{v:+.1f}pt".replace("-", "▲"))
                        case StyleOptions.DataKind.RECORD_DATA_ALL:
                            for prefix in ("p1", "p2", "p3", "p4"):
                                if f"{prefix}_rank" in x.columns:
                                    x[f"{prefix}_rank"] = x[f"{prefix}_rank"].map(lambda v: f"{v:.0f}位")
                                if f"{prefix}_rpoint" in x.columns:
                                    x[f"{prefix}_rpoint"] = x[f"{prefix}_rpoint"].map(lambda v: f"{v:.0f}点".replace("-", "▲"))
                                if f"{prefix}_point" in x.columns:
                                    x[f"{prefix}_point"] = x[f"{prefix}_point"].map(lambda v: f"{v:+.1f}pt".replace("-", "▲"))
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
