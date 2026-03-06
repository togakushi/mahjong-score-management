"""
libs/bootstrap/base_section.py
"""

from pathlib import Path, PosixPath
from types import NoneType
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union

if TYPE_CHECKING:
    from configparser import SectionProxy

    from libs.types import ServiceClassType, SettingClassType, SubCommandsConfigType

SubClassType: TypeAlias = Union[
    "SettingClassType",
    "SubCommandsConfigType",
    "ServiceClassType",
]


class CommonMethodMixin:
    """共通メソッド"""

    _section: "SectionProxy"
    """読み込み先(パーサー + セクション名)"""

    def get(self, key: str, fallback: Any = None) -> Any:
        """値の取得"""
        return self._section.get(key, fallback)

    def getint(self, key: str, fallback: int = 0) -> int:
        """整数値の取得"""
        return self._section.getint(key, fallback)

    def getfloat(self, key: str, fallback: float = 0.0) -> float:
        """数値の取得"""
        return self._section.getfloat(key, fallback)

    def getboolean(self, key: str, fallback: bool = False) -> bool:
        """真偽値の取得"""
        return self._section.getboolean(key, fallback)

    def getlist(self, key: str, fallback: str = "") -> list[str]:
        """リストの取得"""
        return [x.strip() for x in self._section.get(key, fallback).split(",")]

    def keys(self) -> list[str]:
        """キーリストの返却"""
        return list(self._section.keys())

    def values(self) -> list:
        """値リストの返却"""
        return list(self._section.values())

    def items(self) -> list[tuple]:
        """ItemsViewを返却"""
        return list(self._section.items())


class BaseSection(CommonMethodMixin):
    """共通処理"""

    section: str

    def __init__(self, outer: SubClassType, section_name: str):
        self.section = section_name  # セクション名保持
        parser = outer._parser
        assert parser
        if section_name not in parser:
            return
        self._section = parser[section_name]

        self.initialization()

    def __repr__(self) -> str:
        return str({k: v for k, v in vars(self).items() if not str(k).startswith("_")})

    def initialization(self):
        """設定ファイルから値の取り込み"""

        for k in self._section.keys():
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
                    setattr(self, k, self._section.getboolean(k))
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
            drop_items (Optional[list[str]], optional): _description_. Defaults to None.

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
