"""
libs/domain/section.py
"""

import logging
from dataclasses import MISSING, dataclass, field, fields
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union

from libs.types import GradeTableDict

if TYPE_CHECKING:
    from configparser import ConfigParser, SectionProxy

    from integrations.discord.config import SvcConfig as DiscordConfig
    from integrations.slack.config import SvcConfig as SlackConfig
    from integrations.standard_io.config import SvcConfig as StdConfig
    from integrations.web.config import SvcConfig as WebConfig
    from libs.bootstrap.app_config import AppConfig
    from libs.commands.analysis import AnalysisConfig
    from libs.commands.help import HelpConfig
    from libs.commands.registry.member import MemberConfig
    from libs.commands.registry.team import TeamConfig
    from libs.commands.summary import SummaryConfig

ServiceClassType: TypeAlias = Union[
    "SlackConfig",
    "DiscordConfig",
    "WebConfig",
    "StdConfig",
]
"""連携サービスクラス"""

SettingClassType: TypeAlias = Union[
    "SettingSection",
    "MemberConfig",
    "TeamConfig",
    "AliasSection",
    "BadgeDisplay",
    "HelpConfig",
]
"""設定関連クラス"""

CommandClassType: TypeAlias = Union[
    "AnalysisConfig",
    "SummaryConfig",
]
"""コマンド関連クラス"""

SubClassType: TypeAlias = Union[
    "SettingClassType",
    "CommandClassType",
    "ServiceClassType",
]


class CommonMethodMixin:
    """
    共通的な取得メソッドを提供するMixin

    ConfigParser の SectionProxy を介して値を取得するためのユーティリティをまとめる。

    """

    section_proxy: "SectionProxy"
    """読み込み先(パーサー + セクション名)"""

    def get(self, key: str, fallback: Any = None) -> Any:
        """
        値の取得。

        Args:
            key (str): 取得対象のキー。
            fallback (Any, optional): キーが存在しない場合の代替値。

        Returns:
            Any: 取得した値。

        """
        return self.section_proxy.get(key, fallback)

    def getint(self, key: str, fallback: int = 0) -> int:
        """
        整数値の取得。

        Args:
            key (str): 取得対象のキー。
            fallback (int, optional): キーが存在しない場合の代替値。

        Returns:
            int: 取得した整数値。

        """
        return self.section_proxy.getint(key, fallback)

    def getfloat(self, key: str, fallback: float = 0.0) -> float:
        """
        数値の取得。

        Args:
            key (str): 取得対象のキー。
            fallback (float, optional): キーが存在しない場合の代替値。

        Returns:
            float: 取得した浮動小数点値。

        """
        return self.section_proxy.getfloat(key, fallback)

    def getboolean(self, key: str, fallback: bool = False) -> bool:
        """
        真偽値の取得。

        Args:
            key (str): 取得対象のキー。
            fallback (bool, optional): キーが存在しない場合の代替値。

        Returns:
            bool: 取得した真偽値。

        """
        return self.section_proxy.getboolean(key, fallback)

    def getlist(self, key: str, fallback: str = "") -> list[str]:
        """
        カンマ区切り文字列をリストとして取得する。

        Args:
            key (str): 取得対象のキー。
            fallback (str, optional): キーが存在しない場合の代替値。

        Returns:
            list[str]: カンマ区切りを分割して整形した文字列リスト。

        """
        return [x.strip() for x in self.section_proxy.get(key, fallback).split(",")]

    def keys(self) -> list[str]:
        """
        キー一覧を返す。

        Returns:
            list[str]: セクション内のキー一覧。

        """
        return list(self.section_proxy.keys())

    def values(self) -> list[str]:
        """
        値一覧を返す。

        Returns:
            list[str]: セクション内の値一覧。

        """
        return list(self.section_proxy.values())

    def items(self) -> list[tuple[str, str]]:
        """
        キーと値の組を返す。

        Returns:
            list[tuple[str, str]]: セクション内のキー・値ペア一覧。

        """
        return list(self.section_proxy.items())


class BaseSection(CommonMethodMixin):
    """
    基底クラス

    ConfigParser のセクションを読み込み、インスタンス変数へ自動的に値を反映する仕組みを提供する。
    default_reset と after_loading をオーバーライドすることで、読み込み前後の処理を拡張できる。

    """

    section: str
    """セクション名"""
    main_parser: "ConfigParser"
    """設定パーサー"""
    section_proxy: "SectionProxy"
    """読み込み先(パーサー + セクション名)"""

    def __init__(self, outer: SubClassType) -> None:
        """
        設定パーサーから対象セクションを初期化する。

        Args:
            outer (SubClassType): main_parser を保持する外部設定オブジェクト。

        """
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
            drop_items (list[str], optional): 返却に含めないキーリスト。 Defaults to None.

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
    """
    setting セクションの設定値を管理するクラス

    成績管理やグラフ描画、バックアップ設定など、アプリケーション全体の動作に関わる基本設定を保持する。

    """

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
    """
    alias セクションの設定値を管理するクラス

    各種コマンドに対するエイリアス（別名）を保持し、
    設定ファイルから読み込んだ値をもとにコマンド呼び出しを可能にする。

    """

    section: str = "alias"
    """セクション名"""
    summary: list[str] = field(default_factory=lambda: ["summary", "集計"])
    """集計コマンド"""
    analysis: list[str] = field(default_factory=lambda: ["analysis", "分析"])
    """分析コマンド"""
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


class BadgeDisplay(BaseSection):
    """
    バッジ表示に関する設定を管理するクラス
    """

    @dataclass
    class BadgeGradeSpec:
        """
        段位のデータ仕様および参照テーブルを保持するデータクラス

        設定ファイルの ``grade`` セクションから情報を読み込み、段位データの仕様や
        参照するテーブル名を保持する。

        """

        table_name: str = field(default=str())
        """参照する段位テーブルの名前"""
        table: GradeTableDict = field(default_factory=GradeTableDict)
        """段位テーブルのデータを格納する辞書"""

    grade: "BadgeGradeSpec" = BadgeGradeSpec()
    """段位情報"""

    def __init__(self, outer: "AppConfig") -> None:
        """
        BadgeDisplay クラスの初期化。

        AppConfig からパーサーを引き継ぎ、``grade`` セクションが存在する場合は
        設定値を読み込んで grade 属性に設定する。

        Args:
            outer (AppConfig): アプリケーション全体の設定を取りまとめる上位の設定オブジェクト

        """
        self.section = "grade"
        self.main_parser = outer.main_parser

        if self.main_parser.has_section(self.section):
            self.section_proxy = self.main_parser[self.section]
            self.grade.table_name = self.get("table_name", fallback="")
