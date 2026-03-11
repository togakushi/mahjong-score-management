"""
libs/bootstrap/app_config.py
"""

import logging
import sys
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union

from libs.bootstrap.section import AliasSection, BaseSection, MahjongSection, SettingSection
from libs.commands.graph.entry import GraphConfig
from libs.commands.help.entry import HelpConfig
from libs.commands.ranking.entry import RankingConfig
from libs.commands.registry.member import MemberSection
from libs.commands.registry.team import TeamSection
from libs.commands.report.entry import ReportConfig
from libs.commands.results.entry import ResultsConfig
from libs.data.lookup import read_memberslist
from libs.domain.datamodels import CommandType
from libs.domain.rule import RuleSet
from libs.types import GradeTableDict

if TYPE_CHECKING:
    from libs.bootstrap.section import SubCommands
    from libs.types import PlaceholderDict


class DropItems(BaseSection):
    """非表示項目リスト"""

    results: set[str]
    """成績サマリ非表示項目"""
    ranking: set[str]
    """ランキング/レーティング非表示項目"""
    report: set[str]
    """レポート非表示項目"""
    flying: set[str]
    """トビ関連データ非表示指定ワード"""
    yakuman: set[str]
    """役満和了関連データ非表示指定ワード"""
    regulation: set[str]
    """卓外清算関連データ非表示指定ワード"""
    other: set[str]
    """メモ関連データ非表示指定ワード"""

    def __init__(self, outer: "AppConfig") -> None:
        self.main_parser = outer.main_parser

        # 設定値取り込み
        self.section = "results"
        self.section_proxy = self.main_parser[self.section]
        self.results = set(self.getlist("dropitems", fallback=""))

        self.section = "ranking"
        self.section_proxy = self.main_parser[self.section]
        self.ranking = set(self.getlist("dropitems", fallback=""))

        self.section = "report"
        self.section_proxy = self.main_parser[self.section]
        self.report = set(self.getlist("dropitems", fallback=""))

        # 固定ワード
        self.flying = {"トビ", "トビ率"}
        self.yakuman = {"役満", "役満和了", "役満和了率"}
        self.regulation = {"卓外", "卓外清算", "卓外ポイント"}
        self.other = {"その他", "メモ"}


class BadgeDisplay(BaseSection):
    """バッジ表示"""

    @dataclass
    class BadgeGradeSpec:
        """段位"""

        table_name: str = field(default=str())
        table: GradeTableDict = field(default_factory=GradeTableDict)

    grade: "BadgeGradeSpec" = BadgeGradeSpec()
    """段位情報"""

    def __init__(self, outer: "AppConfig") -> None:
        self.section = "grade"
        self.main_parser = outer.main_parser

        if self.main_parser.has_section(self.section):
            self.section_proxy = self.main_parser[self.section]
            self.grade.table_name = self.get("table_name", fallback="")


class AppConfig:
    """アプリケーション設定"""

    def __init__(self, config_file: Path) -> None:
        self.config_file: Path = config_file
        """メイン設定ファイルパス"""

        try:
            self.main_parser: ConfigParser = ConfigParser()
            self.main_parser.read(self.config_file, encoding="utf-8")
        except Exception as err:
            raise RuntimeError(err) from err

        # セクションチェック
        option_sections = [
            "mahjong",
            "setting",
            "results",
            "graph",
            "ranking",
            "report",
            "help",
            "alias",
            "member",
            "team",
            "keyword_mapping",
        ]
        for x in option_sections:
            if x not in self.main_parser.sections():
                self.main_parser.add_section(x)

        # 基本設定
        self.script_dir: Path = Path(sys.argv[0]).absolute().parent
        """スクリプトが保存されているディレクトリパス"""
        self.config_dir: Path = self.config_file.absolute().parent
        """設定ファイルが保存されているディレクトリパス"""
        self.selected_service: Literal["slack", "discord", "web", "standard_io"] = "slack"
        """連携先サービス"""

        # 設定値
        self.setting: SettingSection = SettingSection()
        """settingセクション設定値"""
        self.mahjong: MahjongSection = MahjongSection()
        """mahjongセクション設定値"""
        self.alias: AliasSection = AliasSection()
        """aliasセクション設定値"""

        self.member: MemberSection = MemberSection(self)
        """memberセクション設定値"""
        self.team: TeamSection = TeamSection(self)
        """teamセクション設定値"""

        self.dropitems: DropItems = DropItems(self)
        """非表示項目"""

        self.badge: BadgeDisplay = BadgeDisplay(self)
        """バッジ設定"""

        # サブコマンド
        self.results: "SubCommands" = ResultsConfig()
        """resultsセクション設定値"""
        self.graph: "SubCommands" = GraphConfig()
        """graphセクション設定値"""
        self.ranking: "SubCommands" = RankingConfig()
        """rankingセクション設定値"""
        self.report: "SubCommands" = ReportConfig()
        """reportセクション設定値"""
        self.help: "SubCommands" = HelpConfig()
        """helpセクション設定値"""

        # 共通設定値
        self.aggregate_unit: Literal["A", "M", "Y", None] = None
        """レポート生成用日付範囲デフォルト値(レポート生成用)
        - *A*: 全期間
        - *M*: 月別
        - *Y*: 年別
        - *None*: 未定義
        """

        self.initialization()

        self.rule: RuleSet = RuleSet(self.setting.rule_config)
        """ルール情報"""

    def initialization(self) -> None:
        """設定ファイル読み込み"""
        self.mahjong.config_load(self)
        self.setting.config_load(self)
        self.alias.config_load(self)
        self.member.config_load(self)
        self.team.config_load(self)

        self.results.config_load(self)
        self.graph.config_load(self)
        self.ranking.config_load(self)
        self.report.config_load(self)
        self.help.config_load(self)

    def word_list(self, add_words: list | None = None) -> list[str]:
        """
        設定されている値、キーワードをリスト化する

        Args:
            add_words (list | None, optional): リストに追加するワード. Defaults to None.

        Returns:
            list: リスト化されたキーワード

        """
        words: list[str] = []

        if add_words:
            words.extend(add_words)

        words.extend(list(self.rule.keyword_mapping.keys()))
        words.extend([self.setting.remarks_word])

        for command_name in CommandType:
            if hasattr(self, str(command_name)):
                command = getattr(self, str(command_name))
                if hasattr(command, "default_commandword"):
                    words.append(command.default_commandword)
                if hasattr(command, "commandword"):
                    words.extend(command.commandword)
                if hasattr(command, "command_suffix"):
                    words.extend(command.command_suffix)

        for k, v in self.alias.to_dict().items():
            if isinstance(v, list):
                words.append(k)
                words.extend(v)

        words = [x for x in set(words) if x != ""]  # 重複排除/空文字削除

        return words

    def overwrite(self, additional_config: Path, section_name: str) -> None:
        """
        指定セクションを上書き

        Args:
            additional_config (Path): 追加設定ファイルパス
            section_name (str): セクション名

        """
        if not additional_config.exists():
            return

        try:
            self.additional_config_parser = ConfigParser()
            self.additional_config_parser.read([self.config_file, additional_config], encoding="utf-8")
        except Exception as err:
            logging.error(err)
            return

        protected_values: Union[str, list]
        match section_name:
            case "setting":
                protected_values = self.setting.remarks_word  # 上書き保護
                self.setting.config_load(self)
                self.setting.remarks_word = protected_values
            case "results":
                protected_values = self.results.commandword  # 上書き保護
                self.results.config_load(self)
                self.results.commandword = protected_values
            case "graph":
                protected_values = self.graph.commandword  # 上書き保護
                self.graph.config_load(self)
                self.graph.commandword = protected_values
            case "ranking":
                protected_values = self.ranking.commandword  # 上書き保護
                self.ranking.config_load(self)
                self.ranking.commandword = protected_values
            case "report":
                protected_values = self.report.commandword  # 上書き保護
                self.report.config_load(self)
                self.report.commandword = protected_values
            case _:
                return

    def read_channel_config(self, section_name: str, ret_dict: "PlaceholderDict") -> Optional[Path]:
        """
        チャンネル個別設定読み込み

        Args:
            section_name (str): チャンネル個別設定セクション名
            ret_dict (PlaceholderDict): パラメータ

        Returns:
            Optional[Path]: 個別設定読み込み結果
                - *Path*: 読み込んだ設定ファイルパス
                - *None*: 読み込める設定ファイルがない

        """
        config_path: Optional[Path] = None
        self.initialization()

        if self.main_parser.has_section(section_name):
            if default_rule := self.main_parser[section_name].get("default_rule"):
                ret_dict.update({"default_rule": default_rule})
            if channel_config := self.main_parser[section_name].get("channel_config"):
                config_path = Path(channel_config)
                if config_path.exists():
                    logging.debug("Override: %s", config_path.absolute())
                    self.overwrite(config_path, "setting")
                    self.overwrite(config_path, "results")
                    self.overwrite(config_path, "graph")
                    self.overwrite(config_path, "ranking")
                    self.overwrite(config_path, "report")
                else:
                    config_path = None

        read_memberslist()

        return config_path

    def resolve_channel_id(self, section_name: Optional[str] = None) -> str:
        """
        メイン設定から優先度の高いチャンネルIDを取得する

        Args:
            section_name (Optional[str]): チャンネル個別設定セクション名

        Returns:
            str: チャンネルID

        """
        for section in (section_name, self.selected_service, "setting"):
            if section and self.main_parser.has_section(section):
                if channel_id := self.main_parser[section].get("channel_id"):
                    return channel_id

        if section_name:
            return section_name
        return ""
