"""
libs/utils/converter.py
"""

import textwrap
from typing import TYPE_CHECKING, Any, Optional, Union

import pandas as pd
from table2ascii import Alignment, PresetStyle, table2ascii
from tabulate import tabulate

import libs.global_value as g
from libs.functions import adjusting
from libs.types import StyleOptions
from libs.utils import dictutil, textutil

if TYPE_CHECKING:
    from pathlib import Path

    from libs.types import MessageType


def save_output(
    df: pd.DataFrame,
    options: StyleOptions,
    headline: Optional[tuple["MessageType", StyleOptions]] = None,
    suffix: Optional[str] = None,
) -> Union["Path", None]:
    """
    指定されたフォーマットでdfを保存する

    Args:
        df (pd.DataFrame): 保存対象データ
        options (StyleOptions): 詳細オプション
        headline (tuple[MessageType, StyleOptions], optional): ヘッダコメント. Defaults to None.
        suffix (str, optional): 保存ファイル名に追加する文字列. Defaults to None.

    Returns:
        Union[Path, None]: 保存状態

        - Path: 保存したファイルパス
        - None: ファイル出力なし

    """
    # カラムリネーム
    options.rename_type = StyleOptions.RenameType.NORMAL
    df.rename(columns=dictutil.rename_dicts(df.columns.to_list(), options), inplace=True)
    if options.show_index and isinstance(df.index.name, str):
        if new_index := dictutil.rename_dicts([df.index.name], options).get(df.index.name):
            df.index.name = new_index
    if options.transpose:
        df = df.T

    match options.format_type:
        case "default":
            return None
        case "csv":
            data = df.to_csv(index=options.show_index)
        case "txt":
            data = (
                adjusting.add_units(df)
                .to_markdown(
                    index=options.show_index,
                    tablefmt="outline",
                    floatfmt=adjusting.floatfmt(df, index=options.show_index),
                    colalign=adjusting.column_alignment(df, index=options.show_index),
                    headersalign=adjusting.column_alignment(df, True),
                )
                .replace(" ▲", "▲")
            )

    # 保存
    save_file = textutil.save_file_path(options.filename, True)
    if suffix and g.params.filename:
        save_file = save_file.with_name(f"{save_file.stem}_{suffix}{save_file.suffix}")

    with open(save_file, "w", encoding="utf-8") as writefile:
        # ヘッダコメント書き込み
        if headline:
            headline_data, headline_option = headline
            if options.key_title:
                writefile.writelines(f"# 【{options.title}】\n")
            else:
                writefile.writelines(f"# 【{headline_option.title}】\n")
            if isinstance(headline_data, str):
                for line in headline_data.splitlines():
                    writefile.writelines(f"# {line}\n")
                writefile.writelines("\n")

        # 本文書き込み
        writefile.writelines(data)

    return save_file


def df_to_text_table1(df: pd.DataFrame, options: StyleOptions, max_chars: int = 2000) -> list[str]:
    """
    DataFrameからテキストテーブルの生成

    Args:
        df (pd.DataFrame): 対象データ
        options (StyleOptions): 表示フラグ
        max_chars (int, optional): テーブルに含める最大文字数. Defaults to 2000.

    Returns:
        list[str]: 生成テーブル
    """
    df = adjusting.add_units(df)
    df.rename(columns=dictutil.rename_dicts(df.columns.to_list(), options), inplace=True)

    ret: list[str] = []

    for start, end in textutil.split_markdown_rows(df, max_chars, options.show_index):
        tbl = df[start:end].to_markdown(
            tablefmt="simple",
            index=options.show_index,
            floatfmt=adjusting.floatfmt(df, index=options.show_index),
            headersalign=adjusting.column_alignment(df, header=True, index=options.show_index),
            colalign=adjusting.column_alignment(df, header=False, index=options.show_index),
        )
        if not start and options.key_title:
            if options.codeblock:
                ret.append(f"{options.print_title}\n```\n{tbl}\n```")
            else:
                ret.append(f"{options.print_title}\n{tbl}")
        else:
            ret.append(f"```\n{tbl}\n```" if options.codeblock else tbl)

    return ret


def df_to_text_table2(df: pd.DataFrame, options: StyleOptions, limit: int = 2000) -> list[str]:
    """
    DataFrameからテキストテーブルの生成(縦横変換)

    Args:
        df (pd.DataFrame): 対象データ
        options (StyleOptions): 表示フラグ
        limit (int, optional): 分割文字数. Defaults to 2000.

    Returns:
        list[str]: 生成テーブル

    """
    df.rename(columns=dictutil.rename_dicts(df.columns.to_list(), options), inplace=True)

    # 表生成/分割
    my_style = PresetStyle.plain
    my_style.heading_row_sep = "-"
    my_style.heading_row_right_tee = ""
    my_style.heading_row_left_tee = ""
    my_style.heading_col_sep = "： "

    table_data: list[str] = []
    start_block: int = 0

    safe_output: str = ""
    output: str = ""

    for cur_block in range(len(df.columns) + 1):
        chk_df = df.iloc[:, start_block:cur_block]

        # ヘッダ
        header: list[str] = chk_df.columns.to_list()
        if options.show_index:
            header.insert(0, "")

        # ボディ
        body: list[list[Any]] = []
        data: list[Any] = []
        for idx, item in chk_df.iterrows():
            data.clear()
            data.append(idx)
            data.extend(item.to_list())
            body.append(data.copy())

        output = table2ascii(
            header=header,
            body=body,
            style=my_style,
            cell_padding=0,
            alignments=[Alignment.RIGHT] * len(header),
            first_col_heading=options.show_index,
        )

        # 文字数チェック
        if len(output) < limit:
            safe_output = output
        else:
            table_data.append(f"```\n{safe_output}\n```")
            start_block = cur_block - 1
    # 最終ブロック
    if cur_block <= len(df.columns):
        table_data.append(f"```\n{output}\n```")

    return table_data


def df_to_results_details(df: pd.DataFrame, options: StyleOptions, limit: int = 2000) -> list[str]:
    """
    戦績(詳細)データをテキスト変換

    Args:
        df (pd.DataFrame): 対象データ
        options (StyleOptions): 表示フラグ
        limit (int, optional): 分割文字数. Defaults to 2000.

    Returns:
        list[str]: 整形テキスト

    """
    df = adjusting.add_units(df)
    df.rename(columns=dictutil.rename_dicts(df.columns.to_list(), options), inplace=True)

    data_list: list[str] = []
    game_results: dict[str, dict[str, Any]] = {}

    if options.key_title:
        data_list.append(f"\n{options.print_title}")

    for x in df.to_dict(orient="index").values():
        game_results[x["日時"]] = {"備考": x["備考"]}
        for seat in ("東家", "南家", "西家", "北家"):
            game_results[x["日時"]].update(
                {
                    seat: [
                        x[f"{seat} 名前"],
                        x[f"{seat} 素点"],
                        x[f"{seat} 順位"],
                        x[f"{seat} ポイント"],
                        x[f"{seat} メモ"],
                    ]
                }
            )

    for k, v in game_results.items():
        body = [["　東家："] + v["東家"], ["　南家："] + v["南家"], ["　西家："] + v["西家"], ["　北家："] + v["北家"]]
        output = table2ascii(
            body=body,
            style=PresetStyle.plain,
            cell_padding=0,
            first_col_heading=True,
            alignments=[Alignment.LEFT, Alignment.LEFT, Alignment.RIGHT, Alignment.RIGHT, Alignment.RIGHT, Alignment.LEFT],
        )
        data_list.append(f"{k.replace('-', '/')} {v['備考']}\n" + output + "\n")

    return textutil.join_strings(data_list, limit)


def df_to_results_simple(df: pd.DataFrame, options: StyleOptions, limit: int = 2000) -> list[str]:
    """
    戦績(簡易)データをテキスト変換

    Args:
        df (pd.DataFrame): 対象データ
        options (StyleOptions): 表示フラグ
        limit (int, optional): 分割文字数. Defaults to 2000.

    Returns:
        list[str]: 整形テキスト

    """
    df = adjusting.add_units(df)
    df.rename(columns=dictutil.rename_dicts(df.columns.to_list(), options), inplace=True)

    data_list: list[str] = []

    if options.key_title:
        data_list.append(f"\n{options.print_title}")

    for x in df.to_dict(orient="index").values():
        vs_guest = ""
        if x["備考"] != "":
            vs_guest = f"({g.cfg.setting.guest_mark}) "
        data_list.append(
            f"　{vs_guest}{x['日時']}\t{x['座席']}\t{x['順位']}\t{x['素点']}\t{x['獲得ポイント']}\t{x['メモ']}",
        )

    return textutil.join_strings(data_list, limit)


def df_to_ranking(df: pd.DataFrame, options: StyleOptions, limit: int = 2000) -> list[str]:
    """
    DataFrameからランキングテーブルを生成

    Args:
        df (pd.DataFrame): 対象データ
        options (StyleOptions): 表示フラグ
        limit (int, optional): 分割文字数. Defaults to 2000.

    Returns:
        list[str]: 整形テキスト

    """
    # 表示内容
    body: list[list[Any]] = []
    alignments: list[Alignment] = []

    df = adjusting.add_units(df)

    match options.title:
        case "ゲーム参加率":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.participation_rate,
                        f"({x.count}/{x.total_count}G)",
                    ]
                )
        case "通算ポイント":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.total_point,
                        f"({x.count}G)",
                    ]
                )
        case "平均ポイント":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.avg_point,
                        f"({x.total_point}/{x.count}G)",
                    ]
                )
        case "平均収支":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.avg_balance,
                        f"({x.rpoint_avg}/{x.count}G)",
                    ]
                )
        case "トップ率":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.rank1_rate,
                        f"({x.rank1}/{x.count}G)",
                    ]
                )
        case "連対率":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.top2_rate,
                        f"({x.top2}/{x.count}G)",
                    ]
                )
        case "ラス回避率":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.top3_rate,
                        f"({x.top3}/{x.count}G)",
                    ]
                )
        case "トビ率":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.flying_rate,
                        f"({x.flying}/{x.count}G)",
                    ]
                )
        case "平均順位":
            if g.cfg.rule.get_draw_split(g.params.rule_version):
                alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT]
                for x in df.itertuples():
                    body.append(
                        [
                            f"{x.rank}:",
                            x.name,
                            f"{x.rank_avg}",
                        ]
                    )
            else:
                alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
                for x in df.itertuples():
                    body.append(
                        [
                            f"{x.rank}:",
                            x.name,
                            f"{x.rank_avg}",
                            f"({x.rank_distr}={x.count})".replace("-", "+"),
                        ]
                    )
        case "役満和了率":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.yakuman_rate,
                        f"({x.yakuman}/{x.count}G)",
                    ]
                )
        case "最大素点":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        x.rpoint_max,
                        f"({x.point_max})",
                    ]
                )
        case "連続トップ":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        f"{x.top1_max} / {x.count}G",
                    ]
                )
        case "連続連対":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        f"{x.top2_max} / {x.count}G",
                    ]
                )
        case "連続ラス回避":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        f"{x.top3_max} / {x.count}G",
                    ]
                )
        case "総合ランキング":
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.LEFT]
            for x in df.itertuples():
                body.append(
                    [
                        f"{x.rank}:",
                        x.name,
                        f"（評価点 {x.evaluation}）",
                    ]
                )
        case _:
            return {}

    # 整形/分割
    ret: list[str] = []
    output = table2ascii(
        body=body,
        style=PresetStyle.plain,
        cell_padding=0,
        first_col_heading=True,
        alignments=alignments,
    )

    ranking_data = textutil.split_strings(output, limit)
    for idx, data in enumerate(ranking_data):
        if len(ranking_data) == 1:
            ret.append(f"{options.print_title}\n```\n{data.rstrip()}\n```\n")
            break
        ret.append(f"{options.print_title} ({idx + 1}/{len(ranking_data)})\n```\n{data.rstrip()}\n```\n")

    return ret


def df_to_remarks(df: pd.DataFrame, options: StyleOptions, limit: int = 3000) -> list[str]:
    """
    DataFrameからメモテーブルを生成

    Args:
        df (pd.DataFrame): 対象データ
        options (StyleOptions): 表示フラグ
        limit (int, optional): 分割文字数. Defaults to 3000.

    Returns:
        list[str]: 整形テキスト

    """
    df = adjusting.add_units(df)
    df.rename(columns=dictutil.rename_dicts(df.columns.to_list(), options), inplace=True)

    key_name = "名前" if g.params.individual else "チーム"
    if "日時" in df.columns:
        if "ポイント" in df.columns:
            df["表示"] = df.apply(lambda x: f"{x['日時']} {x['ポイント']} {x['内容']} （{x[key_name]}）", axis=1)
        elif "和了役" in df.columns:
            df["表示"] = df.apply(lambda x: f"{x['日時']} {x['和了役']} （{x[key_name]}）", axis=1)
        else:
            df["表示"] = df.apply(lambda x: f"{x['日時']} {x['内容']} （{x[key_name]}）", axis=1)
    elif "回数" in df.columns:
        if "ポイント" in df.columns:
            df["表示"] = df.apply(lambda x: f"{x['内容']}： {x['回数']} 回 ({x['ポイント合計']})", axis=1)
        elif "和了役" in df.columns:
            df["表示"] = df.apply(lambda x: f"{x['和了役']}： {x['回数']} 回", axis=1)
        else:
            df["表示"] = df.apply(lambda x: f"{x['内容']}： {x['回数']} 回", axis=1)

    #
    rows = tabulate(df.filter(items=["表示"]).values, showindex=False).splitlines()[1:-1]
    tbl = textwrap.indent("\n".join(rows), "\t" * options.indent)
    if options.key_title:
        tbl = f"{options.print_title}\n{tbl}"

    return textutil.split_strings(tbl, limit)
