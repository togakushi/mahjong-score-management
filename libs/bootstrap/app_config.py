"""
libs/bootstrap/app_config.py
"""

import logging
import sys
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Optional, Union

from libs.commands.analysis import AnalysisConfig
from libs.commands.help import HelpConfig
from libs.commands.registry.member import MemberSection
from libs.commands.registry.team import TeamSection
from libs.commands.summary import SummaryConfig
from libs.domain.rule import RuleSet
from libs.domain.section import AliasSection, BadgeDisplay, CommandClassType, SettingSection
from libs.functions.lookup import read_memberslist
from libs.types import CommandType, ServiceType


class AppConfig:
    """
    アプリケーション全体の構成設定と各コマンドセクションを集中管理するクラス。

    設定ファイル（INI形式）の読み込み、不足セクションの自動補完、パスの正規化、
    およびチャンネルごとの個別設定による上書きなどのライフサイクルを一元管理する。

    """

    def __init__(self, config_file: Path) -> None:
        """
        AppConfig クラスの初期化。

        設定ファイルを読み込み、必須セクションの存在チェックと自動生成、
        および各設定セクション・コマンドオブジェクトの構築を行う。

        Args:
            config_file (Path): 読み込むメイン設定ファイルのパス。

        Raises:
            RuntimeError: 設定ファイルの読み込みやパースに失敗した場合。

        """

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
            "summary",
            "analysis",
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
        self.shortcut: dict[str, str] = {}
        """ショートカット格納辞書"""
        self.member: MemberSection = MemberSection(self)
        """memberセクション設定値"""
        self.team: TeamSection = TeamSection(self)
        """teamセクション設定値"""
        self.badge: BadgeDisplay = BadgeDisplay(self)
        """バッジ設定"""

        # コマンド
        self.summary: "CommandClassType" = SummaryConfig()
        """summaryセクション設定値"""
        self.analysis: "CommandClassType" = AnalysisConfig()
        """analysisセクション設定値"""
        self.help: "CommandClassType" = HelpConfig()
        """helpセクション設定値"""

        self.initialization()

        self.rule: RuleSet = RuleSet()
        """ルール情報"""

    def initialization(self) -> None:
        """
        設定ファイルから各セクションのデータを読み込み、パスやフォントの検証を行う。

        フォントファイルの存在チェックを行い、相対パス（作業ディレクトリ、DBパス）を
        適切な絶対パスへ解決する。フォントが見つからない場合はプロセスを異常終了する。

        """
        self.setting.initialization(self.main_parser["setting"])
        self.summary.initialization(self.main_parser["summary"])
        self.analysis.initialization(self.main_parser["analysis"])
        self.alias.initialization(self.main_parser["alias"])
        self.member.initialization(self.main_parser["member"])
        self.team.initialization(self.main_parser["team"])
        self.help.initialization(self.main_parser["help"])

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

        # ショートカット設定取り込み
        if self.main_parser.has_section("shortcut"):
            self.shortcut = dict(self.main_parser.items("shortcut"))

    def word_list(self, add_words: Optional[list[str]] = None) -> list[str]:
        """
        ルール設定、エイリアス、各種コマンドワードを集約したキーワードリストを生成する。

        引数で指定された単語、麻雀ルールのマッピングキー、各サブコマンドの起動ワードや接尾辞、
        および登録されているエイリアスをすべて統合し、重複と空文字を排除して返す。

        Args:
            add_words (Optional[list[str]]): リストに追加したい独自の単語リスト。
                デフォルトは None。

        Returns:
            list[str]: 統合・重複排除されたキーワード文字列のリスト。

        """
        words: list[str] = []

        if add_words:
            words.extend(add_words)

        words.extend(list(self.rule.keyword_mapping.keys()))
        words.extend(self.rule.remarks_words)

        for command_name in CommandType:
            if hasattr(self, str(command_name)):
                if (command := getattr(self, str(command_name))) and hasattr(command, "default_commandword"):
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
        追加の設定ファイルから指定されたセクションの設定を読み込み、上書きする。

        サブコマンドセクション（summary, graph など）を上書きする際、
        既に設定されている ``commandword`` 属性は上書きされないよう保護される。

        Args:
            additional_config (Path): 追加読み込みを行う設定ファイルのパス。
            section_name (str): 上書き対象のセクション名。

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
                self.setting.initialization(additional_config_parser[section_name])
            case "summary":
                if additional_config_parser.has_section(section_name):
                    protected_values = self.summary.commandword  # 上書き保護
                    self.summary.initialization(additional_config_parser[section_name])
                    self.summary.commandword = protected_values
            case "analysis":
                if additional_config_parser.has_section(section_name):
                    protected_values = self.analysis.commandword  # 上書き保護
                    self.analysis.initialization(additional_config_parser[section_name])
                    self.analysis.commandword = protected_values
            case "help":
                protected_values = self.help.commandword  # 上書き保護
                self.help.initialization(additional_config_parser[section_name])
                self.help.commandword = protected_values
            case _:
                return

    def read_channel_config(self, section_name: str, ret_dict: dict[str, Any]) -> Optional[Path]:
        """
        特定のチャンネル専用の設定を読み込み、必要に応じて全体設定をリロードする。

        指定セクションから ``default_rule`` や個別設定ファイルパス（``channel_config``）を取得し、
        ファイルが存在する場合は全体インスタンスの初期化を再実行する。

        Args:
            section_name (str): チャンネル個別の設定が記述されているセクション名。
            ret_dict (dict[str, Any]): 読み込んだパラメータ（default_rule等）を格納・更新する辞書。

        Returns:
            Optional[Path]: 読み込みに成功した場合は個別設定ファイルのパス、
                対象セクションや設定ファイルが存在しない場合は None。

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
                    self.overwrite(config_path, "summary")
                    self.overwrite(config_path, "analysis")
                else:
                    config_path = None

        read_memberslist()

        return config_path

    def resolve_channel_id(self, section_name: Optional[str] = None) -> str:
        """
        メイン設定および個別セクションから優先度の高いチャンネルIDを解決して取得する。

        引数で渡されたセクション名、現在選択されている連携サービス、共通システム設定の順に
        設定ファイルを探索し、最初に見つかった ``channel_id`` を返す。
        いずれのセクションにもIDが定義されておらず、かつ ``section_name`` が指定されている場合は、
        そのセクション名自体をチャンネルIDとみなして返却する。

        Args:
            section_name (Optional[str]): チャンネル個別の設定セクション名。
                デフォルトは None。

        Returns:
            str: 探索により決定されたチャンネルID。
                該当するIDが見つからず、``section_name`` も未指定の場合は空文字を返す。

        """
        for section in (section_name, self.selected_service, "setting"):
            if section and self.main_parser.has_section(section):
                if channel_id := self.main_parser[section].get("channel_id"):
                    return channel_id

        if section_name:
            return section_name
        return ""
