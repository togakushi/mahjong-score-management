"""
libs/domain/rule.py
"""

import logging
import sys
from configparser import ConfigParser
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Mapping

from table2ascii import Alignment, PresetStyle, table2ascii

from libs.domain.command import CommandParser
from libs.utils import dbutil, textutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class RuleData:
    """ルールデータ"""

    # ルール
    rule_version: str = ""
    """ルール識別子"""
    mode: Literal[3, 4] = 4
    """ 集計モード切替(四人打ち/三人打ち)"""
    origin_point: int = 250
    """配給原点"""
    return_point: int = 300
    """返し点"""
    rank_point: list[int] = field(default_factory=list)
    """順位点"""
    ignore_flying: bool = False
    """トビカウント
    - *True*: なし
    - *False*: あり
    """
    draw_split: bool = False
    """同点時の順位点
    - *True*: 山分けにする
    - *False*: 席順で決める
    """
    undefined_word: int = 1
    """未定義ワードタイプ"""
    keywords: list[str] = field(default_factory=list)
    """成績記録キーワード"""
    remarks: list[str] = field(default_factory=list)
    """メモ記録ワード"""
    dropitems: list[str] = field(default_factory=list)
    """非表示にする項目"""

    # ステータス
    first_time: ExtDt = field(default=ExtDt("1900-01-01 00:00:00"))
    """記録開始日時"""
    last_time: ExtDt = field(default=ExtDt("1900-01-01 00:00:00"))
    """最終記録日時"""
    count: int = 0
    """記録回数"""

    def update(self, rule_data: Mapping[str, Any]) -> None:
        """
        ルール更新

        Args:
            rule_data (Mapping): 更新データ

        """
        if "rule_version" in rule_data:
            self.rule_version = str(rule_data["rule_version"])
        if "origin_point" in rule_data:
            self.origin_point = int(rule_data["origin_point"])
        if "return_point" in rule_data:
            self.return_point = int(rule_data["return_point"])

        if rank_point := rule_data.get("rank_point"):
            if isinstance(rank_point, str):
                rank_point = rank_point.split(",")
                self.rank_point = list(map(int, map(float, rank_point[: self.mode])))
            elif isinstance(rank_point, list):
                self.rank_point = list(map(int, map(float, rank_point[: self.mode])))

        if undefined_word := rule_data.get("undefined_word"):
            self.undefined_word = int(undefined_word)
        else:
            self.undefined_word = 1

        for item in ["ignore_flying", "draw_split"]:
            if flag := rule_data.get(item):
                if isinstance(flag, bool):
                    setattr(self, item, flag)
                else:
                    setattr(self, item, str(flag).lower() in {"1", "true", "yes", "on"})

        for item in ["keywords", "remarks", "dropitems"]:
            if item_list := rule_data.get(item):
                if isinstance(item_list, str):
                    setattr(self, item, [x.strip() for x in item_list.split(",")])
                elif isinstance(item_list, list):
                    setattr(self, item, item_list)


class RuleSet:
    """ルールセット"""

    def __init__(self) -> None:
        """ルール設定と派生キャッシュの格納先を初期化する。"""
        self.config: ConfigParser = ConfigParser()
        """ルール設定ファイル"""
        self.data: dict[str, RuleData] = {}
        """ルール情報格納辞書"""
        self.keyword_mapping: dict[str, str] = {}
        """登録キーワードとルール識別子のマッピング"""
        self.remarks_words: list[str] = []
        """メモ記録ワードリスト"""

    def data_set(self, section_name: str, rule_data: Mapping[str, Any]) -> None:
        """
        ルール登録

        Args:
            section_name (str): セクション名
            rule_data (Mapping): 更新データ情報

        """
        rule = RuleData()

        # 初期値セット
        match int(rule_data.get("mode", 4)):
            case 3:
                rule.mode = 3
                rule.origin_point = 350
                rule.return_point = 400
                rule.rank_point = [30, 0, -30]
            case 4:
                rule.mode = 4
                rule.origin_point = 250
                rule.return_point = 300
                rule.rank_point = [30, 10, -10, -30]
            case _:
                logging.warning("Do not register: %s (invalid mode: %s)", section_name, rule_data.get("mode"))
                return

        # 設定値取り込み
        rule.update(rule_data)
        if not rule.rule_version:
            rule.rule_version = section_name
        self.data.update({rule.rule_version: rule})

    def read_config(self, config: "Path") -> None:
        """
        設定ファイル読み込み

        Args:
            config (Path): ルール設定ファイル

        """
        self.config.read(config, encoding="utf-8")
        for section_name in map(str, self.config.sections()):
            if section_name.startswith("regulations_") or section_name.endswith("_regulations"):
                continue
            if section_name.startswith("regulations_team_") or section_name.endswith("_regulations_team"):
                continue

            self.data_set(section_name, dict(self.config[section_name]))

    def status_update(self, params: dict[str, Any]) -> None:
        """
        ステータス更新

        Args:
            params (dict[str, Any]): プレースホルダ

        """
        # ステータスリセット
        for rule_version in self.rule_list:
            self.data[rule_version].count = 0
            self.data[rule_version].first_time.set("1900-01-01 00:00:00")
            self.data[rule_version].last_time.set("1900-01-01 00:00:00")

        status = dbutil.execute(
            """
            select
                rule_version,
                min(ts) as first_time,
                max(ts) as last_time,
                count() as count
            from
                result
            --[separate] where source = :source
            group by
                rule_version
            ;
            """,
            params,
        )

        # ステータス更新
        for status_data in status:
            if (rule_version := str(status_data.get("rule_version", ""))) and self.data.get(rule_version):
                if "count" in status_data:
                    self.data[rule_version].count = int(status_data["count"])
                if "first_time" in status_data:
                    self.data[rule_version].first_time = ExtDt(float(status_data["first_time"]))
                if "last_time" in status_data:
                    self.data[rule_version].last_time = ExtDt(float(status_data["last_time"]))

    def remarks_words_update(self, suffix: list[str]) -> None:
        """
        メモ記録ワードリストを更新する

        Args:
            suffix (list[str]): メモに追加するサフィックス

        """
        ret: list[str] = []

        for rule in self.rule_list:
            if rule_data := self.data.get(rule):
                if rule_data.remarks:
                    ret.extend(rule_data.remarks)
                else:
                    ret.extend(
                        [f"{pre}{suf}" for pre in self.keywords(rule) for suf in suffix],
                    )

        self.remarks_words = list(set(ret))

    def to_dict(self, rule_version: str) -> dict[str, Any]:
        """
        指定ルール識別子の情報を辞書で返す

        Args:
            rule_version (str): ルール識別子

        Returns:
            dict[str, Any]: ルール情報

        """
        if rule := self.data.get(rule_version):
            return {
                "rule_version": rule.rule_version,
                "mode": rule.mode,
                "origin_point": rule.origin_point,
                "return_point": rule.return_point,
                "rank_point": rule.rank_point,
                "ignore_flying": rule.ignore_flying,
                "draw_split": rule.draw_split,
                "undefined_word": rule.undefined_word,
            }

        return {}

    def keywords(self, rule_version: str) -> set[str]:
        """
        成績記録キーワードの取得

        Args:
            rule_version (str): ルール識別子

        Returns:
            set[str]: 成績記録キーワード

        """
        if items := self.data.get(rule_version):
            return set(items.keywords)
        else:
            return set([])

    def dropitems(self, rule_version: str) -> set[str]:
        """
        非表示項目の取得

        Args:
            rule_version (str): ルール識別子

        Returns:
            set[str]: 非表示項目

        """
        if items := self.data.get(rule_version):
            return set(items.dropitems)
        else:
            return set([])

    def get_version(self, mode: int, mapping: bool = True) -> list[str]:
        """
        指定した条件のルール識別子をリストで返す

        Args:
            mode (int): 集計モード
            mapping (bool, optional): Defaults to True.

                - *True*: キーワードマッピングに登録されているルールのみ
                - *False*: ルールとして定義されているものすべて

        Returns:
            list[str]: ルール識別子

        """
        ret: list[str] = []

        for keyword, rule in self.data.items():
            if rule.mode == mode:
                if mapping:
                    if keyword in self.keyword_mapping.values():
                        ret.append(rule.rule_version)
                else:
                    ret.append(rule.rule_version)

        return ret

    def get_mode(self, rule_version: str) -> int:
        """
        指定ルール識別子の集計モードを返す

        Args:
            rule_version (str): ルール識別子

        Returns:
            int: 集計モード

        """
        return int(self.to_dict(rule_version).get("mode", 0))

    def get_ignore_flying(self, rule_version: str) -> bool:
        """
        指定ルール識別子のトビカウントフラグを返す

        Args:
            rule_version (str): ルール識別子

        Returns:
            bool: トビカウントフラグ

        """
        return bool(self.to_dict(rule_version).get("ignore_flying", False))

    def get_draw_split(self, rule_version: str) -> bool:
        """
        指定ルール識別子の順位点山分けフラグを返す

        Args:
            rule_version (str): ルール識別子

        Returns:
            bool: 順位点山分けフラグ

        """
        return bool(self.to_dict(rule_version).get("draw_split", False))

    def get_undefined_word(self, rule_version: str) -> int:
        """
        指定ルール識別子の未定義ワードタイプを返す

        Args:
            rule_version (str): ルール識別子

        Returns:
            int: 未定義ワードタイプ

        """
        return int(self.to_dict(rule_version).get("undefined_word", 1))

    def print(self, rule_version: str) -> str:
        """
        指定ルール識別子の内容を出力する

        Args:
            rule_version (str): ルール識別子

        Returns:
            str: 内容

        """
        ret: str = ""
        body_data: list[list[str]] = []

        if rule := self.data.get(rule_version):
            body_data.append(["ルール識別子", rule.rule_version])

            # 集計モード
            match rule.mode:
                case 3:
                    body_data.append(["集計モード", "三人打ち"])
                case 4:
                    body_data.append(["集計モード", "四人打ち"])
                case _:
                    body_data.append(["集計モード", "未定義"])

            body_data.extend(
                [
                    ["素点", f"{rule.origin_point * 100}点持ち / {rule.return_point * 100}点返し"],
                    ["順位点", " / ".join([f"{pt}pt".replace("-", "▲") for pt in rule.rank_point])],
                    ["同点時", "順位点山分け" if rule.draw_split else "席順"],
                ]
            )

            # マッピング情報
            if keyword := [word for word, mapping_rule in self.keyword_mapping.items() if mapping_rule == rule_version]:
                body_data.append(["成績記録キーワード", "、".join(keyword)])
            else:
                body_data.append(["成績記録キーワード", "---"])

            # 記録時間
            body_data.append(["記録数", f"{rule.count} ゲーム"])
            if rule.count:
                body_data.extend(
                    [
                        ["記録開始日時", rule.first_time.format(ExtDt.FMT.YMDHMS)],
                        ["最終記録日時", rule.last_time.format(ExtDt.FMT.YMDHMS)],
                    ]
                )

            ret = table2ascii(
                body=body_data,
                alignments=[Alignment.LEFT, Alignment.LEFT],
                style=PresetStyle.plain,
            )

        return ret

    def info(self) -> None:
        """定義ルールをログに出力する"""
        for rule in self.data.values():
            logging.info(
                "%s: mode=%s, origin_point=%s, return_point=%s, rank_point=%s, draw_split=%s, ignore_flying=%s, undefined_word=%s",
                rule.rule_version,
                rule.mode,
                rule.origin_point,
                rule.return_point,
                rule.rank_point,
                rule.draw_split,
                rule.ignore_flying,
                rule.undefined_word,
            )
        if self.keyword_mapping:
            logging.info("keyword_mapping: %s", self.keyword_mapping)
        else:
            logging.warning("keyword_mapping: empty")
        if self.remarks_words:
            logging.info("remarks_words: %s", self.remarks_words)
        else:
            logging.warning("remarks_words: empty")

    def check(self, chk_commands: set[str], chk_members: set[str], default_rule: str) -> None:
        """
        キーワード重複チェック

        Args:
            chk_commands (set[str]): チェック対象コマンド名
            chk_members (set[str]): チェック対象メンバー名/チーム名
            default_rule (str): デフォルトルールバージョン

        Raises:
            RuntimeError: 重複あり

        """
        chk_word: str | RuleData

        # チェックパターン生成
        name_pattern: list[str] = []
        for name in chk_members:
            name_pattern.append(name)
            name_pattern.append(textutil.str_conv(name, textutil.ConversionType.KtoH))  # ひらがな
            name_pattern.append(textutil.str_conv(name, textutil.ConversionType.HtoK))  # カタカナ

        try:
            # ルール識別子チェック
            for chk_word in self.data.values():
                if CommandParser().is_valid_command(chk_word.rule_version):
                    raise RuntimeError(f"ルール識別子にオプションに使用される単語が使用されています。({chk_word.rule_version})")
                if chk_word.rule_version in ExtDt.valid_keywords():
                    raise RuntimeError(f"ルール識別子に検索範囲指定に使用される単語が使用されています。({chk_word.rule_version})")
                if chk_word.rule_version in chk_commands:
                    raise RuntimeError(f"ルール識別子と定義済みコマンドに重複があります。({chk_word.rule_version})")
                if textutil.name_replace(chk_word.rule_version, not_replace=True) in set(name_pattern):
                    raise RuntimeError(f"ルール識別子と登録メンバー(チーム)に重複があります。({chk_word.rule_version})")
            # 成績記録キーワードチェック
            for chk_word in self.keyword_mapping.keys():
                if CommandParser().is_valid_command(chk_word):
                    raise RuntimeError(f"成績記録キーワードにオプションに使用される単語が使用されています。({chk_word})")
                if chk_word in ExtDt.valid_keywords():
                    raise RuntimeError(f"成績記録キーワードに検索範囲指定に使用される単語が使用されています。({chk_word})")
                if chk_word in chk_commands:
                    raise RuntimeError(f"成績記録キーワードと定義済みコマンドに重複があります。({chk_word})")
                if textutil.name_replace(chk_word, not_replace=True) in set(name_pattern):
                    raise RuntimeError(f"成績記録キーワードと登録メンバー(チーム)に重複があります。({chk_word})")
            # デフォルトルールバージョンチェック
            if default_rule not in self.rule_list:
                raise RuntimeError(f"デフォルトルールバージョンに指定されているルールセットが見つかりません。({default_rule})")
        except RuntimeError as err:
            logging.critical("%s", err)
            sys.exit(1)

    def register_to_database(self) -> None:
        """ルールセット情報をDBに登録する"""
        dbutil.execute("delete from rule;")
        for rule in self.rule_list:
            params = self.to_dict(rule)
            params.update(rank_point=" ".join(map(str, params["rank_point"])))
            dbutil.execute(
                """
                insert into
                rule (
                    rule_version, mode, origin_point, return_point, rank_point, ignore_flying, draw_split, undefined_word
                ) values (
                    :rule_version, :mode, :origin_point, :return_point, :rank_point, :ignore_flying, :draw_split, :undefined_word
                );
                """,
                params,
            )

    @property
    def rule_list(self) -> list[str]:
        """
        定義済みルール識別子の列挙

        Returns:
            list[str]: ルール識別子

        """
        return [x.rule_version for x in self.data.values()]
