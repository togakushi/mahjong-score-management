"""libs/bootstrap/section.py
"""

import logging
import sys
from pathlib import Path, PosixPath
from types import NoneType
from typing import TYPE_CHECKING, Any, Literal, Optional, TypeAlias, Union

from libs.domain.datamodels import CommandAttrs

if TYPE_CHECKING:
    from configparser import ConfigParser, SectionProxy

    from libs.bootstrap.app_config import AppConfig
    from libs.types import ServiceClassType, SettingClassType

SubClassType: TypeAlias = Union[
    "SettingClassType",
    "SubCommands",
    "ServiceClassType",
]


class CommonMethodMixin:
    """共通メソッド"""

    section_proxy: "SectionProxy"
    """読み込み先(パーサー + セクション名)"""

    def get(self, key: str, fallback: Any = None) -> Any:
        """値の取得"""
        return self.section_proxy.get(key, fallback)

    def getint(self, key: str, fallback: int = 0) -> int:
        """整数値の取得"""
        return self.section_proxy.getint(key, fallback)

    def getfloat(self, key: str, fallback: float = 0.0) -> float:
        """数値の取得"""
        return self.section_proxy.getfloat(key, fallback)

    def getboolean(self, key: str, fallback: bool = False) -> bool:
        """真偽値の取得"""
        return self.section_proxy.getboolean(key, fallback)

    def getlist(self, key: str, fallback: str = "") -> list[str]:
        """リストの取得"""
        return [x.strip() for x in self.section_proxy.get(key, fallback).split(",")]

    def keys(self) -> list[str]:
        """キーリストの返却"""
        return list(self.section_proxy.keys())

    def values(self) -> list:
        """値リストの返却"""
        return list(self.section_proxy.values())

    def items(self) -> list[tuple]:
        """ItemsViewを返却"""
        return list(self.section_proxy.items())


class BaseSection(CommonMethodMixin):
    """基底クラス"""

    section: str
    """セクション名"""
    main_parser: "ConfigParser"
    """設定パーサー"""
    section_proxy: "SectionProxy"
    """読み込み先(パーサー + セクション名)"""

    def __init__(self, outer: SubClassType):
        self.main_parser = outer.main_parser
        assert self.main_parser
        if not hasattr(self, "section") or self.section not in self.main_parser:
            return
        self.section_proxy = self.main_parser[self.section]

        self.initialization()

    def __repr__(self) -> str:
        return str({k: v for k, v in vars(self).items() if not str(k).startswith("_")})

    def initialization(self):
        """設定ファイルから値の取り込み"""
        for k in self.section_proxy.keys():
            if k not in self.to_dict():
                continue  # インスタンス変数と一致しない項目はスキップ
            match type(self.__dict__.get(k)):
                case v_type if k in self.__dict__ and v_type is str:
                    setattr(self, k, self.get(k))
                case v_type if k in self.__dict__ and v_type is int:
                    setattr(self, k, self.getint(k))
                case v_type if k in self.__dict__ and v_type is float:
                    setattr(self, k, self.getfloat(k))
                case v_type if v_type is bool:
                    setattr(self, k, self.section_proxy.getboolean(k))
                case v_type if k in self.__dict__ and v_type is list:
                    v_list = self.getlist(k)
                    current_list = getattr(self, k)
                    if isinstance(current_list, list) and current_list:  # 設定済みリストは追加
                        current_list.extend(v_list)
                    else:
                        setattr(self, k, v_list)
                case v_type if k in self.__dict__ and v_type is Optional[str]:  # 文字列 or None(未定義)
                    setattr(self, k, self.get(k))
                case v_type if k in self.__dict__ and v_type is PosixPath:
                    setattr(self, k, Path(self.get(k)))
                case v_type if k in self.__dict__ and v_type is NoneType:
                    if k in ["backup_dir"]:  # ディレクトリを指定する設定はPathで格納
                        setattr(self, k, Path(self.get(k)))
                    else:
                        setattr(self, k, self.get(k))
                case _:
                    setattr(self, k, self.__dict__.get(k))

    def to_dict(self, drop_items: Optional[list[str]] = None) -> dict[str, str]:
        """必要なパラメータを辞書型で返す

        Args:
            drop_items (Optional[list[str]], optional): 返却に含めないキーリスト. Defaults to None.

        Returns:
             dict[str, str]: 返却値

        """
        ret_dict: dict[str, str] = {}
        for key in vars(self):
            if key.startswith("_"):
                continue
            ret_dict[key] = getattr(self, key)

        if drop_items:
            for item in drop_items:
                if item in ret_dict:
                    ret_dict.pop(item)

        return ret_dict


class MahjongSection(BaseSection):
    """mahjongセクション処理"""

    def __init__(self):
        self.section: str = "mahjong"
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
        self.main_parser = outer.main_parser
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

    keyword: str
    """成績記録キーワード(プライマリ)"""
    remarks_word: str
    """メモ記録用キーワード"""
    remarks_suffix: list[str]
    """メモ記録用キーワードサフィックス"""
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
        self.section: str = "setting"
        self._reset()

    def _reset(self):
        self.keyword = str("終局")
        self.remarks_word = str("麻雀メモ")
        self.remarks_suffix = []
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
        self.main_parser = outer.main_parser
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
        self.section = "alias"
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
        self.main_parser = outer.main_parser
        self._reset()
        super().__init__(self)

        # delのエイリアス取り込み(設定ファイルに`delete`と書かれていない)
        self.delete.extend(self.getlist("del", fallback="del"))

        logging.debug("%s: %s", self.section, self)


class SubCommands(BaseSection, CommandAttrs):
    """サブコマンドセクション処理"""

    default_commandword: str
    """コマンドワードデフォルト値"""

    def config_load(self, outer: "AppConfig"):
        """設定値取り込み

        Args:
            outer (AppConfig): 設定クラスオブジェクト

        """
        self.main_parser = outer.main_parser
        self.section_proxy = outer.main_parser[self.section]
        self.default_reset()
        super().__init__(self)

        # 呼び出しキーワード取り込み
        self.commandword = self.getlist("commandword", self.default_commandword)

        logging.debug("%s: %s", self.section, self)
