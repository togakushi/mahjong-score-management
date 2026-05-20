"""
libs/bootstrap/section.py
"""

import logging
from dataclasses import MISSING, dataclass, field, fields
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union

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

        # 設定値取り込み前の初期化処理
        if (reset_method := getattr(self, "default_reset", None)) and callable(reset_method):
            reset_method()

        for k in self.section_proxy.keys():
            if k not in self.to_dict():
                continue  # インスタンス変数と一致しない項目はスキップ
            current_value = self.__dict__.get(k)
            match current_value:
                case _ if k in self.__dict__ and isinstance(current_value, str):
                    setattr(self, k, self.get(k))
                case _ if isinstance(current_value, bool):
                    setattr(self, k, self.section_proxy.getboolean(k))
                case _ if k in self.__dict__ and isinstance(current_value, int):
                    setattr(self, k, self.getint(k))
                case _ if k in self.__dict__ and isinstance(current_value, float):
                    setattr(self, k, self.getfloat(k))
                case _ if k in self.__dict__ and isinstance(current_value, list):
                    v_list = self.getlist(k)
                    if current_value:  # 設定済みリストは追加
                        current_value.extend(v_list)
                    else:
                        setattr(self, k, v_list)
                case _ if k in self.__dict__ and isinstance(current_value, Path):
                    setattr(self, k, Path(self.get(k)))
                case None if k in self.__dict__:
                    if k in ["backup_dir", "rule_config"]:  # Optional[Path]
                        setattr(self, k, Path(self.get(k)))
                    else:
                        setattr(self, k, self.get(k))
                case _:
                    setattr(self, k, current_value)

        # 設定値取り込み後の追加処理
        if (after_method := getattr(self, "after_loading", None)) and callable(after_method):
            after_method()

        logging.trace("%s: %s", self.section, self)  # type: ignore

    def to_dict(self, drop_items: Optional[list[str]] = None) -> dict[str, str]:
        """
        必要なパラメータを辞書型で返す

        Args:
            drop_items (list[str], optional): 返却に含めないキーリスト. Defaults to None.

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


@dataclass
class SettingSection(BaseSection):
    """settingセクション処理"""

    section: str = "setting"
    """セクション名"""
    remarks_suffix: list[str] = field(default_factory=list)
    """メモ記録用キーワードサフィックス"""
    rule_config: Optional[Path] = field(default=None)
    """ルール設定ファイル"""
    default_rule: str = field(default="")
    """ルール識別子未指定時に使用される識別子"""
    separate: bool = field(default=False)
    """スコア入力元識別子別集計フラグ
    - *True*: 識別子別に集計
    - *False*: すべて集計
    """
    channel_id: Optional[str] = field(default=None)
    """チャンネルIDを上書きする"""
    time_adjust: int = field(default=12)
    """日付変更後、集計範囲に含める追加時間"""
    search_word: str = field(default="")
    """コメント固定(検索時の検索文字列)"""
    group_length: int = field(default=0)
    """コメント固定(検索時の集約文字数)"""
    guest_mark: str = field(default="※")
    """ゲスト無効時に未登録メンバーに付与する印"""
    database_file: Union[str, Path] = field(default=Path("mahjong.db"))
    """成績管理データベースファイル名"""
    backup_dir: Optional[Path] = field(default=None)
    """バックアップ先ディレクトリ"""
    font_file: Path = field(default=Path("ipaexg.ttf"))
    """グラフ描写に使用するフォントファイル"""
    graph_style: str = field(default="ggplot")
    """グラフスタイル"""
    work_dir: Path = field(default=Path("work"))
    """作業ディレクトリ"""

    def default_reset(self) -> None:
        """デフォルト値にリセット"""
        for f in fields(self):
            if f.default is not MISSING:
                setattr(self, f.name, f.default)
            elif f.default_factory is not MISSING:
                setattr(self, f.name, f.default_factory())


@dataclass
class AliasSection(BaseSection):
    """aliasセクション処理"""

    section: str = "alias"
    """セクション名"""
    results: list[str] = field(default_factory=lambda: ["results", "成績"])
    """成績サマリ出力コマンド"""
    graph: list[str] = field(default_factory=lambda: ["graph", "グラフ"])
    """成績グラフ出力コマンド"""
    ranking: list[str] = field(default_factory=lambda: ["ranking", "ランキング"])
    """ランキング出力コマンド"""
    report: list[str] = field(default_factory=lambda: ["report", "レポート"])
    """レポート出力コマンド"""
    download: list[str] = field(default_factory=lambda: ["download", "ダウンロード"])
    """DBダウンロードコマンド"""
    member: list[str] = field(default_factory=lambda: ["member", "userlist", "member_list"])
    """メンバーリスト表示コマンド"""
    add: list[str] = field(default_factory=lambda: ["add"])
    """メンバー追加コマンド"""
    delete: list[str] = field(default_factory=lambda: ["del"])
    """メンバー削除コマンド"""
    team_create: list[str] = field(default_factory=lambda: ["team_create"])
    """チーム作成コマンド"""
    team_del: list[str] = field(default_factory=lambda: ["team_del"])
    """チーム削除コマンド"""
    team_add: list[str] = field(default_factory=lambda: ["team_add"])
    """チーム所属コマンド"""
    team_remove: list[str] = field(default_factory=lambda: ["team_remove"])
    """チーム脱退コマンド"""
    team_list: list[str] = field(default_factory=lambda: ["team_list"])
    """チームリスト出力コマンド"""
    team_clear: list[str] = field(default_factory=lambda: ["team_clear"])
    """全チーム情報削除コマンド"""

    def after_loading(self) -> None:
        """AliasSection専用の追加処理"""

        # delのエイリアス取り込み(設定ファイルに ``delete`` と書かれていない)
        self.delete.extend(self.getlist("del", fallback="del"))


class SubCommands(BaseSection, CommandAttrs):
    """サブコマンドセクション処理"""

    default_commandword: str
    """コマンドワードデフォルト値"""
