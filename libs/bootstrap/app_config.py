"""
libs/bootstrap/config.py
"""

import logging
import sys
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, Union

from libs.bootstrap.base_section import BaseSection
from libs.commands.graph.entry import GraphConfig
from libs.commands.help.entry import HelpConfig
from libs.commands.ranking.entry import RankingConfig
from libs.commands.registry.configuration import MemberSection, TeamSection
from libs.commands.report.entry import ReportConfig
from libs.commands.results.entry import ResultsConfig
from libs.data.lookup import read_memberslist
from libs.domain.rule import RuleSet
from libs.types import GradeTableDict


class MahjongSection(BaseSection):
    """mahjongセクション処理"""

    def __init__(self):
        self.mode: Literal[3, 4] = 4
        """ 集計モード切替(四人打ち/三人打ち)"""
        self.rule_version: str = str("default_rule")
        """ルール識別子"""
        self.origin_point: int = int(-1)
        """配給原点"""
        self.return_point: int = int(-1)
        """返し点"""
        self.rank_point: list = []
        """順位点"""
        self.ignore_flying: bool = False
        """トビカウント
        - *True*: なし
        - *False*: あり
        """
        self.draw_split: bool = False
        """同点時の順位点
        - *True*: 山分けにする
        - *False*: 席順で決める
        """
        self.undefined_word = 0
        """未定義ワードタイプ"""

    def config_load(self, outer: "AppConfig"):
        """設定値取り込み

        Args:
            outer (AppConfig): 設定クラスオブジェクト
        """

        self.section: str = "mahjong"
        self._parser = outer._parser
        super().__init__(self)

        # デフォルト値
        match self.mode:
            case 3:
                if self.origin_point < 0:
                    self.origin_point = 350
                if self.return_point < 0:
                    self.return_point = 400
                if not self.rank_point:
                    self.rank_point = [30, 0, -30]
            case 4:
                if self.origin_point < 0:
                    self.origin_point = 250
                if self.return_point < 0:
                    self.return_point = 300
                if not self.rank_point:
                    self.rank_point = [30, 10, -10, -30]

        self.rank_point = self.rank_point[: self.mode]

        logging.debug("%s: %s", self.section, self)


class SettingSection(BaseSection):
    """settingセクション処理"""

    help: str
    """ヘルプ表示キーワード"""
    keyword: str
    """成績記録キーワード(プライマリ)"""
    remarks_word: str
    """メモ記録用キーワード"""
    rule_config: Path
    """ルール設定ファイル"""
    default_rule: str
    """ルール識別子未指定時に使用される識別子"""
    separate: bool
    """スコア入力元識別子別集計フラグ
    - *True*: 識別子別に集計
    - *False*: すべて集計
    """
    channel_id: Optional[str]
    """チャンネルIDを上書きする"""
    time_adjust: int
    """日付変更後、集計範囲に含める追加時間"""
    search_word: str
    """コメント固定(検索時の検索文字列)"""
    group_length: int
    """コメント固定(検索時の集約文字数)"""
    guest_mark: str
    """ゲスト無効時に未登録メンバーに付与する印"""
    database_file: Union[str, Path]
    """成績管理データベースファイル名"""
    backup_dir: Optional[Path]
    """バックアップ先ディレクトリ"""
    font_file: Path
    """グラフ描写に使用するフォントファイル"""
    graph_style: str
    """グラフスタイル"""
    work_dir: Path

    def __init__(self):
        self._reset()

    def _reset(self):
        self.help = str("麻雀成績ヘルプ")
        self.keyword = str("終局")
        self.remarks_word = str("麻雀成績メモ")
        self.rule_config = Path("files/default_rule.ini")
        self.time_adjust = int(12)
        self.default_rule = str("")
        self.separate = bool(False)
        self.channel_id = None
        self.search_word = str("")
        self.group_length = int(0)
        self.guest_mark = str("※")
        self.database_file = Path("mahjong.db")
        self.backup_dir = None
        self.font_file = Path("ipaexg.ttf")
        self.graph_style = str("ggplot")
        self.work_dir = Path("work")

    def config_load(self, outer: "AppConfig"):
        """設定値取り込み

        Args:
            outer (AppConfig): 設定クラスオブジェクト
        """

        self.section: str = "setting"
        self._parser = outer._parser
        self._reset()
        super().__init__(self)

        # 成績登録キーワード
        if not (isinstance(self.keyword, Path) and self.keyword.exists()):
            self.keyword = str(self.keyword)

        # デフォルトルール識別子
        if not self.default_rule:
            self.default_rule = outer.mahjong.rule_version

        # フォントファイルチェック
        for chk_dir in (outer.config_dir, outer.script_dir):
            chk_file = chk_dir / str(self.font_file)
            if chk_file.exists():
                self.font_file = chk_file
                break
        else:
            if not self.font_file.exists():
                logging.critical("The specified font file cannot be found.")
                sys.exit(255)

        # 作業ディレクトリパス
        if not self.work_dir.is_absolute():
            self.work_dir = outer.script_dir / self.work_dir

        # データベース関連
        if isinstance(self.database_file, Path) and not self.database_file.exists():
            self.database_file = outer.config_dir / str(self.database_file)

        logging.debug("%s: %s", self.section, self)


class AliasSection(BaseSection):
    """aliasセクション処理"""

    results: list
    """成績サマリ出力コマンド"""
    graph: list
    """成績グラフ出力コマンド"""
    ranking: list
    """ランキング出力コマンド"""
    report: list
    """レポート出力コマンド"""
    download: list
    member: list
    """メンバーリスト表示コマンド"""
    add: list
    delete: list
    team_create: list
    team_del: list
    team_add: list
    team_remove: list
    team_list: list
    """チームリスト出力コマンド"""
    team_clear: list

    def __init__(self):
        self._reset()

    def _reset(self):
        self.results = ["results", "成績"]
        self.graph = ["graph", "グラフ"]
        self.ranking = ["ranking", "ランキング"]
        self.report = ["report", "レポート"]
        self.download = ["download", "ダウンロード"]
        self.member = ["member", "userlist", "member_list"]
        self.add = ["add"]
        self.delete = ["del"]
        self.team_create = ["team_create"]
        self.team_del = ["team_del"]
        self.team_add = ["team_add"]
        self.team_remove = ["team_remove"]
        self.team_list = ["team_list"]
        self.team_clear = ["team_clear"]

    def config_load(self, outer: "AppConfig"):
        """設定値取り込み

        Args:
            outer (AppConfig): 設定クラスオブジェクト
        """

        self.section: str = "alias"
        self._parser = outer._parser
        self._reset()
        super().__init__(self)

        # delのエイリアス取り込み(設定ファイルに`delete`と書かれていない)
        list_data = [x.strip() for x in str(self._parser.get("alias", "del", fallback="del")).split(",")]
        self.delete.extend(list_data)

        logging.debug("%s: %s", self.section, self)


class DropItems(BaseSection):
    """非表示項目リスト"""

    def __init__(self, outer: "AppConfig"):
        self._parser = outer._parser

        # 設定値取り込み
        super().__init__(self)
        self.results: set = {x.strip() for x in self._parser.get("results", "dropitems", fallback="").split(",")}
        """成績サマリ非表示項目"""
        self.ranking: set = {x.strip() for x in self._parser.get("ranking", "dropitems", fallback="").split(",")}
        """ランキング/レーティング非表示項目"""
        self.report: set = {x.strip() for x in self._parser.get("report", "dropitems", fallback="").split(",")}
        """レポート非表示項目"""

        # 固定ワード
        self.flying = {"トビ", "トビ率"}
        """トビ関連データ非表示指定ワード"""
        self.yakuman = {"役満", "役満和了", "役満和了率"}
        """役満和了関連データ非表示指定ワード"""
        self.regulation = {"卓外", "卓外清算", "卓外ポイント"}
        """卓外清算関連データ非表示指定ワード"""
        self.other = {"その他", "メモ"}
        """メモ関連データ非表示指定ワード"""


class BadgeDisplay(BaseSection):
    """バッジ表示"""

    @dataclass
    class BadgeGradeSpec:
        """段位"""

        table_name: str = field(default=str())
        table: GradeTableDict = field(default_factory=GradeTableDict)

    grade: "BadgeGradeSpec" = BadgeGradeSpec()

    def __init__(self, outer: "AppConfig"):
        self._parser = outer._parser
        super().__init__(self)

        self.grade.table_name = self._parser.get("grade", "table_name", fallback="")


class AppConfig:
    """コンフィグ解析クラス"""

    def __init__(self, config_file: Path):
        self.config_file = config_file
        try:
            self.main_parser = ConfigParser()
            self.main_parser.read(self.config_file, encoding="utf-8")
            self._parser = self.main_parser
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
            if x not in self._parser.sections():
                self._parser.add_section(x)

        # 基本設定
        self.script_dir = Path(sys.argv[0]).absolute().parent
        """スクリプトが保存されているディレクトリパス"""
        self.config_dir = self.config_file.absolute().parent
        """設定ファイルが保存されているディレクトリパス"""
        self.selected_service: Literal["slack", "discord", "web", "standard_io"] = "slack"
        """連携先サービス"""

        # 設定値
        self.setting = SettingSection()
        """settingセクション設定値"""
        self.mahjong = MahjongSection()
        """mahjongセクション設定値"""
        self.alias = AliasSection()
        """aliasセクション設定値"""

        self.member = MemberSection()
        """memberセクション設定値"""
        self.team = TeamSection()
        """teamセクション設定値"""

        self.dropitems = DropItems(self)
        """非表示項目"""

        self.badge = BadgeDisplay(self)
        """バッジ設定"""

        # サブコマンド
        self.results = ResultsConfig()
        """resultsセクション設定値"""
        self.graph = GraphConfig()
        """graphセクション設定値"""
        self.ranking = RankingConfig()
        """rankingセクション設定値"""
        self.report = ReportConfig()
        """reportセクション設定値"""
        self.help = HelpConfig()
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

    def initialization(self):
        """設定ファイル読み込み"""

        self._parser = self.main_parser

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

    def word_list(self) -> list[str]:
        """設定されている値、キーワードをリスト化する

        Returns:
            list: リスト化されたキーワード
        """

        words: list[str] = []
        words.extend(self.results.commandword)
        words.extend(self.graph.commandword)
        words.extend(self.ranking.commandword)
        words.extend(self.report.commandword)
        words.extend(list(self.rule.keyword_mapping.keys()))
        words.extend([self.setting.remarks_word])

        for k, v in self.alias.to_dict().items():
            if isinstance(v, list):
                words.append(k)
                words.extend(v)

        words = [x for x in set(words) if x != ""]  # 重複排除/空文字削除

        return words

    def overwrite(self, additional_config: Path, section_name: str):
        """指定セクションを上書き

        Args:
            additional_config (Path): 追加設定ファイルパス
            section_name (str): セクション名
        """

        if not additional_config.exists():
            return

        try:
            self._parser = ConfigParser()
            self._parser.read([self.config_file, additional_config], encoding="utf-8")
        except Exception as err:
            logging.error(err)
            return

        protected_values: Union[str, list]
        match section_name:
            case "setting":
                protected_values = self.setting.help  # 上書き保護
                self.setting.config_load(self)
                self.setting.help = protected_values
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

    def read_channel_config(self, section_name: str) -> Optional[Path]:
        """チャンネル個別設定読み込み

        Args:
            section_name (str): セクション名

        Returns:
            Optional[Path]: 個別設定読み込み結果
                - *Path*: 読み込んだ設定ファイルパス
                - *None*: 読み込める設定ファイルがない
        """

        config_path: Optional[Path] = None
        self.initialization()

        if self.main_parser.has_section(section_name):
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
        """メイン設定から優先度の高いチャンネルIDを取得する

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
