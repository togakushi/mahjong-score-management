"""
libs/bootstrap/app_config.py
"""

import logging
import sys
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

from libs.bootstrap.section import AliasSection, BaseSection, SettingSection, SubCommands
from libs.commands.graph.entry import GraphConfig
from libs.commands.help.entry import HelpConfig
from libs.commands.ranking.entry import RankingConfig
from libs.commands.registry.member import MemberSection
from libs.commands.registry.team import TeamSection
from libs.commands.report.entry import ReportConfig
from libs.commands.results.entry import ResultsConfig
from libs.domain.rule import RuleSet
from libs.functions.lookup import read_memberslist
from libs.types import CommandType, GradeTableDict, ServiceType


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

    @dataclass
    class FixedWords:
        """非表示項目用固定ワード"""

        flying: set[str] = field(default_factory=lambda: {"トビ", "トビ率"})
        """トビ関連ワード"""
        yakuman: set[str] = field(default_factory=lambda: {"役満", "役満和了", "役満和了率"})
        """役満関連ワード"""
        regulation: set[str] = field(default_factory=lambda: {"卓外", "卓外清算", "卓外ポイント"})
        """レギュレーション関連ワード"""
        other: set[str] = field(default_factory=lambda: {"その他", "メモ"})
        """その他ワード"""

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
            "setting",
            "results",
            "graph",
            "ranking",
            "report",
            "help",
            "alias",
            "member",
            "team",
        ]
        for x in option_sections:
            if x not in self.main_parser.sections():
                self.main_parser.add_section(x)

        # 基本設定
        self.script_dir: Path = Path(sys.argv[0]).absolute().parent
        """スクリプトが保存されているディレクトリパス"""
        self.config_dir: Path = self.config_file.absolute().parent
        """設定ファイルが保存されているディレクトリパス"""
        self.selected_service: ServiceType = ServiceType.SLACK
        """連携先サービス"""

        # 設定値
        self.setting: SettingSection = SettingSection()
        """settingセクション設定値"""
        self.alias: AliasSection = AliasSection()
        """aliasセクション設定値"""
        self.member: MemberSection = MemberSection(self)
        """memberセクション設定値"""
        self.team: TeamSection = TeamSection(self)
        """teamセクション設定値"""
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

        self.initialization()

        self.dropitems = self.FixedWords()
        """非表示項目リスト"""
        self.rule: RuleSet = RuleSet()
        """ルール情報"""

    def initialization(self) -> None:
        """設定ファイル読み込み"""
        self.setting.config_load(self.main_parser["setting"])
        self.alias.config_load(self.main_parser["alias"])
        self.member.config_load(self.main_parser["member"])
        self.team.config_load(self.main_parser["team"])

        self.results.config_load(self.main_parser["results"])
        self.graph.config_load(self.main_parser["graph"])
        self.ranking.config_load(self.main_parser["ranking"])
        self.report.config_load(self.main_parser["report"])
        self.help.config_load(self.main_parser["help"])

        # フォントファイルチェック
        for chk_dir in (self.config_dir, self.script_dir):
            chk_file = chk_dir / str(self.setting.font_file)
            if chk_file.exists():
                self.setting.font_file = chk_file
                break
        else:
            if not self.setting.font_file.exists():
                logging.critical("The specified font file cannot be found.")
                sys.exit(255)

        # 作業ディレクトリパス
        if not self.setting.work_dir.is_absolute():
            self.setting.work_dir = self.script_dir / self.setting.work_dir

        # データベース関連
        if isinstance(self.setting.database_file, Path) and not self.setting.database_file.exists():
            self.setting.database_file = self.config_dir / str(self.setting.database_file)

    def word_list(self, add_words: Optional[list[str]] = None) -> list[str]:
        """
        設定されている値、キーワードをリスト化する

        Args:
            add_words (list[str], optional): リストに追加するワード. Defaults to None.

        Returns:
            list[str]: リスト化されたキーワード

        """
        words: list[str] = []

        if add_words:
            words.extend(add_words)

        words.extend(list(self.rule.keyword_mapping.keys()))
        words.extend(self.rule.remarks_words)

        for command_name in CommandType:
            if hasattr(self, str(command_name)):
                if (command := getattr(self, str(command_name))) and isinstance(command, SubCommands):
                    words.append(command.default_commandword)
                    words.extend(command.commandword)
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
            additional_config_parser = ConfigParser()
            additional_config_parser.read([self.config_file, additional_config], encoding="utf-8")
        except Exception as err:
            logging.error(err)
            return

        protected_values: Union[str, list[str]]
        match section_name:
            case "setting":
                self.setting.config_load(additional_config_parser[section_name])
            case "results":
                protected_values = self.results.commandword  # 上書き保護
                self.results.config_load(additional_config_parser[section_name])
                self.results.commandword = protected_values
            case "graph":
                protected_values = self.graph.commandword  # 上書き保護
                self.graph.config_load(additional_config_parser[section_name])
                self.graph.commandword = protected_values
            case "ranking":
                protected_values = self.ranking.commandword  # 上書き保護
                self.ranking.config_load(additional_config_parser[section_name])
                self.ranking.commandword = protected_values
            case "report":
                protected_values = self.report.commandword  # 上書き保護
                self.report.config_load(additional_config_parser[section_name])
                self.report.commandword = protected_values
            case "help":
                protected_values = self.help.commandword  # 上書き保護
                self.help.config_load(additional_config_parser[section_name])
                self.help.commandword = protected_values
            case _:
                return

    def read_channel_config(self, section_name: str, ret_dict: dict[str, Any]) -> Optional[Path]:
        """
        チャンネル個別設定読み込み

        Args:
            section_name (str): チャンネル個別設定セクション名
            ret_dict (dict[str, Any]): パラメータ

        Returns:
            Optional[Path]: 個別設定読み込み結果

            - *Path*: 読み込んだ設定ファイルパス
            - *None*: 読み込める設定ファイルがない

        """
        config_path: Optional[Path] = None

        if self.main_parser.has_section(section_name):
            if default_rule := self.main_parser[section_name].get("default_rule"):
                ret_dict.update({"default_rule": default_rule})
            if channel_config := self.main_parser[section_name].get("channel_config"):
                config_path = Path(channel_config)
                if config_path.exists():
                    logging.debug("Override: %s", config_path.absolute())
                    self.initialization()
                    self.overwrite(config_path, "setting")
                    self.overwrite(config_path, "results")
                    self.overwrite(config_path, "graph")
                    self.overwrite(config_path, "ranking")
                    self.overwrite(config_path, "report")
                    self.overwrite(config_path, "help")
                else:
                    config_path = None

        read_memberslist()

        return config_path

    def resolve_channel_id(self, section_name: Optional[str] = None) -> str:
        """
        メイン設定から優先度の高いチャンネルIDを取得する

        Args:
            section_name (str, optional): チャンネル個別設定セクション名

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
