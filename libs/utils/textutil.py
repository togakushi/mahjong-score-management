"""
libs/utils/textutil.py
"""

import os
import random
import re
from enum import Enum, auto
from typing import TYPE_CHECKING

import pandas as pd

import libs.global_value as g

if TYPE_CHECKING:
    from pathlib import Path


class ConversionType(Enum):
    """変換タイプ"""

    HtoZ = auto()
    """半角文字を全角文字に変換(数字のみ)"""
    ZtoH = auto()
    """全角文字を半角文字に変換(数字のみ)"""
    HtoK = auto()
    """ひらがなをカタカナに変換"""
    KtoH = auto()
    """カタカナをひらがなに変換"""


def name_replace(target: str, add_mark: bool = False, guest_replace: bool = True) -> str:
    """
    表記ブレ修正(正規化)

    Args:
        target (str): 対象プレイヤー名
        add_mark (bool, optional): ゲストマークを付与する。 Defaults to False.
        guest_replace (bool, optional): 未登録メンバーをゲストに置換する。 Defaults to True.

    Returns:
        str: 表記ブレ修正後のプレイヤー名

    """
    if g.params.anonymous and (ret_name := g.params.mapping_dict.get(target)):
        return ret_name

    chk_pattern = [
        target,  # 無加工
        str_conv(target, ConversionType.HtoZ),  # 半角 -> 全角
        str_conv(target, ConversionType.KtoH),  # カタ -> ひら
        str_conv(target, ConversionType.HtoK),  # ひら -> カタ
        honor_remove(target),  # 敬称削除
        honor_remove(str_conv(target, ConversionType.HtoZ)),  # 敬称削除 + 半角 -> 全角
        honor_remove(str_conv(target, ConversionType.KtoH)),  # 敬称削除 + カタ -> ひら
        honor_remove(str_conv(target, ConversionType.HtoK)),  # 敬称削除 + ひら -> カタ
    ]
    chk_pattern = sorted(set(chk_pattern), key=chk_pattern.index)  # 順序を維持したまま重複排除

    if g.params.individual or not guest_replace:
        for name in chk_pattern:
            if name in g.cfg.member.lists:  # メンバーリスト
                return name
            if name in g.cfg.member.all_lists:  # 別名を含むリスト
                if ret_name := g.cfg.member.resolve_name(name):
                    return ret_name
    else:
        for team in chk_pattern:
            if team in g.cfg.team.lists:  # チームリスト
                return team

    # リストに見つからない場合
    name = honor_remove(target)
    if g.params.unregistered_replace and guest_replace:
        name = g.cfg.member.guest_name
    if name != g.cfg.member.guest_name and add_mark:
        name = f"{name}({g.cfg.setting.guest_mark})"

    return name


def honor_remove(name: str) -> str:
    """
    敬称削除

    Args:
        name (str): 対象の名前

    Returns:
        str: 敬称を削除した名前

    """
    honor = r"(くん|さん|ちゃん|クン|サン|チャン|君)$"
    if re.match(rf".*{honor}", name):
        if not re.match(rf".*(っ|ッ|ー){honor}", name):
            name = re.sub(rf"{honor}", "", name)

    return name


def anonymous_mapping(name_list: list[str], initial: int = 0) -> dict[str, str]:
    """
    名前リストから変換用辞書を生成

    Args:
        name_list (list[str]): 名前リスト
        initial (int, optional): インデックス初期値. Defaults to 0.

    Returns:
        dict[str, str]: マッピング用辞書

    """
    ret: dict[str, str] = {}

    if g.params.individual:
        prefix = "Player"
        id_list = {x["name"]: x["id"] for x in g.cfg.member.info}
    else:
        prefix = "Team"
        id_list = {x["team"]: x["id"] for x in g.cfg.team.info}

    if len(name_list) == 1:
        name = name_list[0]
        if name in id_list:
            idx = id_list[name]
        else:
            idx = int(random.random() * 100 + 100)
        ret[name] = f"{prefix}_{idx + initial:03d}"
    else:
        random.shuffle(name_list)
        for idx, name in enumerate(name_list):
            ret[name] = f"{prefix}_{idx + initial:03d}"

    return ret


def str_conv(text: str, kind: ConversionType) -> str:
    """
    文字列変換

    Args:
        text (str): 変換対象文字列
        kind (ConversionType): 変換種類

    Returns:
        str: 変換後の文字列

    """
    zen = "".join(chr(0xFF10 + i) for i in range(10))
    han = "".join(chr(0x30 + i) for i in range(10))
    hira = "".join(chr(0x3041 + i) for i in range(86))
    kana = "".join(chr(0x30A1 + i) for i in range(86))

    match kind:
        case ConversionType.HtoZ:
            trans_table = str.maketrans(han, zen)
        case ConversionType.ZtoH:
            trans_table = str.maketrans(zen, han)
        case ConversionType.HtoK:
            trans_table = str.maketrans(hira, kana)
        case ConversionType.KtoH:
            trans_table = str.maketrans(kana, hira)
        case _:
            return text

    return text.translate(trans_table)


def save_file_path(filename: str, delete: bool = False) -> "Path":
    """
    保存ファイルのフルパスを取得

    Args:
        filename (str): デフォルトファイル名
        delete (bool, optional): 生成済みファイルを削除. Defaults to False.

    Returns:
        Path: 保存ファイルパス

    """
    _, file_ext = os.path.splitext(filename)
    file_name = f"{g.params.filename}{file_ext}" if g.params.filename else f"{filename}"
    file_path = g.cfg.setting.work_dir / file_name

    if file_path.exists() and delete:
        os.remove(file_path)

    return file_path


def split_text_blocks(text: str, limit: int = 2000) -> list[str]:
    """
    指定文字数でテキストを行単位で分割してリストにする

    Args:
        text (str): 対象文字列
        limit (int, optional): 分割文字数. Defaults to 2000.

    Returns:
        list[str]: 分割リスト

    """
    blocks: list[str] = []
    current_data = ""
    buffer_data = ""
    in_code = False
    min_gap_after_code_start = 10
    lines_count = 0

    for _, line in enumerate(text.splitlines(keepends=True)):
        stripped = line.strip()
        buffer_data += line

        # --- コードブロック開始／終了検出 ---
        if stripped.startswith("```"):
            in_code = not in_code
            if not in_code:
                current_data += buffer_data
                buffer_data = ""
            continue

        lines_count += 1 if in_code else 0

        # --- 文字数チェック ---
        if len(current_data + buffer_data) > limit:
            if lines_count > min_gap_after_code_start:
                if in_code:
                    blocks.append(current_data + buffer_data + "```\n")
                    buffer_data = "```\n"
                else:
                    blocks.append(current_data + buffer_data)
                    buffer_data = ""
            else:
                blocks.append(current_data)  # 先頭の改行は削除されてしまう
            current_data = ""

    return blocks


def split_strings(msg: str, limit: int = 3000) -> list[str]:
    """
    指定文字数で分割

    Args:
        msg (str): 分割対象
        limit (int, optional): 分割文字数. Defaults to 3000.

    Returns:
        list[str]: 分割結果

    """
    result: list[str] = []
    buffer: list[str] = []
    codeblock: bool = False

    for line in msg.splitlines(keepends=True):
        # 仮に追加したときの文字列長を計算
        temp = buffer + [line]
        total_len = len("".join(temp))

        if total_len < limit:
            buffer.append(line)
            if line != line.replace("```", ""):  # 1行でopen/closeされる想定ではない
                codeblock = not (codeblock)
        else:
            if buffer:
                if codeblock:  # codeblock open状態
                    buffer.append("```\n")
                    result.append("".join(buffer))
                    buffer = [f"```\n{line}"]
                else:
                    result.append("".join(buffer))
                    buffer = [line]

    if result:
        return result
    return [msg]


def group_strings(lines: list[str], limit: int = 3000) -> list[str]:
    """
    指定文字数まで改行で連結

    Args:
        lines (list[str]): 連結対象
        limit (int, optional): 制限値. Defaults to 3000.

    Returns:
        list[str]: 連結結果

    """
    result: list[str] = []
    buffer: list[str] = []

    for i, line in enumerate(lines):
        is_last = i == len(lines) - 1  # 最終ブロック判定
        max_char = limit * 1.5 if is_last else limit  # 1ブロックの最大値

        # 仮に追加したときの文字列長を計算
        temp = buffer + [line]
        total_len = len("".join(temp))

        if total_len <= max_char:
            buffer.append(line)
        else:
            if buffer:
                result.append("\n".join(buffer))
            buffer = [line]

    if buffer:
        result.append("\n".join(buffer))

    # 改行の集約
    result = [str(x).replace("\n```\n\n```\n", "\n```\n```\n") for x in result]
    result = [str(x).replace("\n\n\t", "\n\t") for x in result]

    return result


def split_markdown_rows(
    df: pd.DataFrame,
    max_chars: int,
    index: bool = True,
) -> list[tuple[int, int]]:
    """
    DataFrameをMarkdownテーブルの文字数制限に合わせて分割する。

    Args:
        df: 分割対象のDataFrame。
        max_chars: 1テーブルあたりの最大文字数。
        index: MarkdownテーブルにDataFrameのindexを含めるか。

    Raises:
        ValueError: max_charsが0以下の場合。
        ValueError: 1行だけでも文字数制限を超える場合。
        RuntimeError: 最小分割数で解なしの場合。

    Returns:
        list[tuple[int, int]]: 各テーブルの開始行番号と終了番号のペア

    """
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")

    n = len(df)

    if n == 0:
        return [(0, 0)]

    # 各範囲の文字数キャッシュ / (start, end): start <= row < end
    cache: dict[tuple[int, int], int] = {}

    def markdown_length(start: int, end: int) -> int:
        key = (start, end)

        if key not in cache:
            cache[key] = len(
                df.iloc[start:end].to_markdown(
                    index=index,
                    tablefmt="simple",
                )
            )

        return cache[key]

    # ------------------------------------------------------------
    # 最小分割数
    # ------------------------------------------------------------
    boundaries = [0]
    start = 0

    while start < n:
        end = start + 1

        if markdown_length(start, end) > max_chars:
            raise ValueError(f"row {start + 1} cannot fit within max_chars={max_chars}")

        while end < n and markdown_length(start, end + 1) <= max_chars:
            end += 1

        boundaries.append(end)
        start = end

    block_count = len(boundaries) - 1

    if block_count == 1:
        return [(0, n)]

    # ------------------------------------------------------------
    # 均等化
    # ------------------------------------------------------------
    dp: dict[tuple[int, int], tuple[int, int | None]] = {(0, 0): (0, None)}

    for k in range(1, block_count + 1):
        # k個のブロックでendまで分割する。
        for end in range(k, n + 1):
            best: tuple[int, int] | None = None
            for start in range(k - 1, end):
                previous = dp.get((k - 1, start))

                if previous is None:
                    continue

                length = markdown_length(start, end)

                if length > max_chars:
                    continue

                cost = previous[0] + length**2

                if best is None or cost < best[0]:
                    best = (cost, start)

            if best is not None:
                dp[(k, end)] = best

    # 最小分割数で解が存在することを確認。
    if (block_count, n) not in dp:
        raise RuntimeError("failed to find a valid partition")

    # ------------------------------------------------------------
    # 分割位置を復元
    # ------------------------------------------------------------
    ranges: list[tuple[int, int]] = []
    end = n

    for k in range(block_count, 0, -1):
        _, split_start = dp[(k, end)]

        assert split_start is not None

        ranges.append((split_start, end))
        end = split_start

    ranges.reverse()

    return ranges


def join_strings(strings: list[str], max_chars: int = 2000) -> list[str]:
    """
    文字列を改行で連結し、文字数制限に応じて分割する。

    Args:
        strings: 連結対象の文字列。
        max_chars: 1ブロックあたりの最大文字数。

    Returns:
        連結後の文字列のリスト。

    Raises:
        ValueError: max_charsが0以下の場合。
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")

    if not strings:
        return []

    # 各文字列単体の長さ
    lengths = [len(s) for s in strings]

    # 文字列を1つ以上含むブロックの文字数(start:end の文字列を "\n".join() した長さ)
    def block_length(start: int, end: int) -> int:
        return sum(lengths[start:end]) + (end - start - 1)

    n = len(strings)

    # ------------------------------------------------------------
    # 最小ブロック数
    # ------------------------------------------------------------
    dp = [float("inf")] * (n + 1)
    dp[0] = 0

    for end in range(1, n + 1):
        for start in range(end):
            length = block_length(start, end)
            if length <= max_chars or start == end - 1:
                dp[end] = min(dp[end], dp[start] + 1)

    block_count = int(dp[n])

    # ------------------------------------------------------------
    # 均等化
    # ------------------------------------------------------------
    dp2: dict[tuple[int, int], tuple[int, int | None]] = {
        (0, 0): (0, None),
    }

    for count in range(1, block_count + 1):
        for end in range(count, n + 1):
            best: tuple[int, int] | None = None

            for start in range(count - 1, end):
                previous = dp2.get((count - 1, start))

                if previous is None:
                    continue

                length = block_length(start, end)

                if length > max_chars and start != end - 1:
                    continue

                cost = previous[0] + length**2

                if best is None or cost < best[0]:
                    best = (cost, start)

            if best is not None:
                dp2[(count, end)] = best

    # ------------------------------------------------------------
    # 分割位置を復元
    # ------------------------------------------------------------
    ranges: list[tuple[int, int]] = []
    end = n

    for count in range(block_count, 0, -1):
        _, split_start = dp2[(count, end)]

        assert split_start is not None

        ranges.append((split_start, end))
        end = split_start

    ranges.reverse()

    return ["\n".join(strings[start:end]) for start, end in ranges]
