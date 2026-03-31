"""
libs/bootstrap/section.py
"""

import logging
from pathlib import Path, PosixPath
from types import NoneType
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union, get_args, get_origin

from libs.domain.datamodels import CommandAttrs

if TYPE_CHECKING:
    from configparser import ConfigParser, SectionProxy

    from integrations.discord.config import SvcConfig as DiscordConfig
    from integrations.slack.config import SvcConfig as SlackConfig
    from integrations.standard_io.config import SvcConfig as StdConfig
    from integrations.web.config import SvcConfig as WebConfig
    from libs.bootstrap.app_config import BadgeDisplay
    from libs.commands.registry.member import MemberSection
    from libs.commands.registry.team import TeamSection

ServiceClassType: TypeAlias = Union[
    "SlackConfig",
    "DiscordConfig",
    "WebConfig",
    "StdConfig",
]
"""連携サービスクラス"""

SettingClassType: TypeAlias = Union[
    "SettingSection",
    "MemberSection",
    "TeamSection",
    "AliasSection",
    "BadgeDisplay",
]
"""設定関連クラス"""

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

    def values(self) -> list[str]:
        """値リストの返却"""
        return list(self.section_proxy.values())

    def items(self) -> list[tuple[str, str]]:
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

    def __init__(self, outer: SubClassType) -> None:
        self.main_parser = outer.main_parser
        assert self.main_parser
        if not hasattr(self, "section") or self.section not in self.main_parser:
            return

        self.initialization(self.main_parser[self.section])

    def __repr__(self) -> str:
        return str({k: v for k, v in vars(self).items() if not str(k).startswith("_")})

    def initialization(self, section_proxy: "SectionProxy") -> None:
        """
        設定ファイルから値の取り込み

        Args:
            section_proxy (SectionProxy): 読み込み先(パーサー + セクション名)

        """
        self.section_proxy = section_proxy
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
                case v_type if k in self.__dict__ and get_origin(v_type) is Union and type(None) in get_args(v_type):  # 文字列 or None(未定義)
                    setattr(self, k, self.get(k))
                case v_type if k in self.__dict__ and v_type is PosixPath:
                    setattr(self, k, Path(self.get(k)))
                case v_type if k in self.__dict__ and v_type is NoneType:
                    if k in ["backup_dir", "rule_config"]:  # Optional[Path]
                        setattr(self, k, Path(self.get(k)))
                    else:
                        setattr(self, k, self.get(k))
                case _:
                    setattr(self, k, self.__dict__.get(k))

    def _before_config_load(self) -> None:
        """設定値取り込み前の初期化処理"""
        if (reset_method := getattr(self, "default_reset", None)) and callable(reset_method):
            reset_method()

    def _after_config_load(self, _section_proxy: "SectionProxy") -> None:
        """設定値取り込み後の追加処理"""

    def config_load(self, section_proxy: "SectionProxy") -> None:
        """設定値取り込み"""
        self._before_config_load()
        self.initialization(section_proxy)
        self._after_config_load(section_proxy)

        logging.trace("%s: %s", self.section, self)  # type: ignore

    def to_dict(self, drop_items: Optional[list[str]] = None) -> dict[str, str]:
        """
        必要なパラメータを辞書型で返す

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


class SettingSection(BaseSection):
    """settingセクション処理"""

    remarks_word: str
    """メモ記録用キーワード"""
    remarks_suffix: list[str]
    """メモ記録用キーワードサフィックス"""
    rule_config: Optional[Path]
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
    """作業ディレクトリ"""

    def __init__(self) -> None:
        self.section: str = "setting"
        self.default_reset()

    def default_reset(self) -> None:
        """パラメータ初期化"""
        self.remarks_word = str("麻雀メモ")
        self.remarks_suffix = []
        self.rule_config = None
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


class AliasSection(BaseSection):
    """aliasセクション処理"""

    results: list[str]
    """成績サマリ出力コマンド"""
    graph: list[str]
    """成績グラフ出力コマンド"""
    ranking: list[str]
    """ランキング出力コマンド"""
    report: list[str]
    """レポート出力コマンド"""
    download: list[str]
    member: list[str]
    """メンバーリスト表示コマンド"""
    add: list[str]
    delete: list[str]
    team_create: list[str]
    team_del: list[str]
    team_add: list[str]
    team_remove: list[str]
    team_list: list[str]
    """チームリスト出力コマンド"""
    team_clear: list[str]

    def __init__(self) -> None:
        self.section = "alias"
        self.default_reset()

    def default_reset(self) -> None:
        """パラメータ初期化"""
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

    def _after_config_load(self, _section_proxy: "SectionProxy") -> None:
        """AliasSection専用の追加処理"""

        # delのエイリアス取り込み(設定ファイルに`delete`と書かれていない)
        self.delete.extend(self.getlist("del", fallback="del"))


class SubCommands(BaseSection, CommandAttrs):
    """サブコマンドセクション処理"""

    default_commandword: str
    """コマンドワードデフォルト値"""
