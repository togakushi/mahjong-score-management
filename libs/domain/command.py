"""
libs/domain/command.py
"""

import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Callable, Literal, TypedDict, Union

import pandas as pd

from libs.domain.datamodels import ParameterData
from libs.utils import formatter, textutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

CommandResult = Mapping[str, Union[str, int, bool, tuple[str, ...]]]
"""コマンド処理結果の型（パラメータ名とその値のマッピング）"""
CommandAction = Callable[[Union[str, tuple[str, ...]]], CommandResult]
"""コマンド処理関数の型（入力文字列を受け取り、結果辞書を返す）"""


class CommandSpec(TypedDict, total=False):
    """コマンドマッピングテーブル"""

    match: list[str]
    action: CommandAction
    type: Literal["int", "str", "sql", "filename"]


CommandsDict = dict[str, CommandSpec]
COMMANDS: CommandsDict = {
    # --- ゲスト処理
    "guest_off": {
        "match": [r"^ゲストナシ$"],
        "action": lambda _: {"guest_skip": False, "guest_skip2": False, "unregistered_replace": True},
    },
    "guest_on": {
        "match": [r"^ゲストアリ$"],
        "action": lambda _: {"guest_skip": True, "guest_skip2": True, "unregistered_replace": True},
    },
    # --- 個人戦/チーム戦
    "individual": {
        "match": [r"^個人$", "^個人成績$"],
        "action": lambda _: {"individual": True},
    },
    "team": {
        "match": [r"^チーム$", "^チーム成績$", "^team$"],
        "action": lambda _: {"individual": False},
    },
    "all_player": {
        "match": [r"^全員$", r"^all$"],
        "action": lambda _: {"all_player": True},
    },
    "a": {
        "match": [r"^(チーム同卓アリ|コンビアリ|同士討チ)$"],
        "action": lambda _: {"friendly_fire": True},
    },
    "b": {
        "match": [r"^(チーム同卓ナシ|コンビナシ)$"],
        "action": lambda _: {"friendly_fire": False},
    },
    # --- プレイヤー名変換処理
    "guest_disable": {
        "match": [r"^ゲスト無効$"],
        "action": lambda _: {"unregistered_replace": False},
    },
    "anonymous": {
        "match": [r"^匿名$", r"^anonymous$"],
        "action": lambda _: {"anonymous": True},
    },
    # --- 動作変更フラグ
    "score_comparisons": {  # 比較
        "match": [r"^比較$", r"^点差$", r"^差分$"],
        "action": lambda _: {"score_comparisons": True},
    },
    "order": {  # 順位出力
        "match": [r"^順位$"],
        "action": lambda _: {"order": True},
    },
    "results": {  # 戦績
        "match": [r"^戦績$"],
        "action": lambda _: {"game_results": True},
    },
    "versus": {  # 対戦結果
        "match": [r"^対戦結果$", r"^対戦$"],
        "action": lambda _: {"versus_matrix": True},
    },
    "statistics": {  # 統計
        "match": [r"^統計$"],
        "action": lambda _: {"statistics": True},
    },
    "rating": {  # レーティング
        "match": [r"^レート$", r"^レーティング$", r"^rate$", r"^ratings?$"],
        "action": lambda _: {"rating": True},
    },
    "verbose": {  # 詳細
        "match": [r"^詳細$", r"^verbose$"],
        "action": lambda _: {"verbose": True},
    },
    # --- 集計条件
    "ranked": {
        "match": [r"^(トップ|上位|top)(\d*)$"],
        "action": lambda w: {"ranked": w},
    },
    "stipulated": {
        "match": [r"^(規定数|規定打数)(\d*)$"],
        "action": lambda w: {"stipulated": w},
    },
    "interval": {
        "match": [r"^(期間|区間|区切リ?|interval)(\d*)$"],
        "action": lambda w: {"interval": w},
    },
    # --- 集約 / 検索条件
    "daily": {
        "match": [r"^daily$", r"^日次$", r"^デイリー$"],
        "action": lambda _: {"collection": "daily"},
    },
    "weekly": {
        "match": [r"^weekly$", r"^週次$", r"^ウイークリー$"],
        "action": lambda _: {"collection": "weekly"},
    },
    "monthly": {
        "match": [r"^monthly$", r"^月次$", r"^マンスリー$"],
        "action": lambda _: {"collection": "monthly"},
    },
    "yearly": {
        "match": [r"^yearly$", r"^年次$", r"^イヤーリー$"],
        "action": lambda _: {"collection": "yearly"},
    },
    "collection": {
        "match": [r"^全体$"],
        "action": lambda _: {"collection": "all"},
    },
    "comment": {
        "match": [r"^(コメント|comment)(.*)$"],
        "action": lambda w: {"search_word": w},
        "type": "sql",
    },
    "grouping": {
        "match": [r"^(集約)(\d*)$"],
        "action": lambda w: {"group_length": w},
    },
    "mode3": {
        "match": [r"^三人打ち$", r"^三人打$", r"^三麻$", r"^サンマ$"],
        "action": lambda _: {"target_mode": 3},
    },
    "mode4": {
        "match": [r"^四人打ち$", r"^四人打$", r"^四麻$", r"^ヨンマ$"],
        "action": lambda _: {"target_mode": 4},
    },
    "most_recent": {
        "match": [r"^(直近)(\d*)$"],
        "action": lambda w: {"target_count": w},
    },
    "mixed": {
        "match": [r"^横断$", r"^mix$", r"^mixed$"],
        "action": lambda _: {"mixed": True},
    },
    # --- 出力オプション
    "format": {
        "match": [r"^(csv|text|txt)$"],
        "action": lambda w: {"format": w if w != "text" else "txt"},
        "type": "str",
    },
    "filename": {
        "match": [r"^(filename:|ファイル名)(.*)$"],
        "action": lambda w: {"filename": w},
        "type": "filename",
    },
}


@dataclass
class ParsedCommand:
    """コマンド解析結果"""

    flags: dict[str, Any]
    """真偽値、引数を持つオプションを格納"""
    arguments: list[str]
    """単独オプションを格納"""
    unknown: list[str]
    """オプションと認識されない文字列を格納（プレイヤー名候補）"""
    search_range: list[ExtDt]
    """検索範囲の日時を格納"""


class CommandParser:
    """引数解析クラス"""

    def __init__(self) -> None:
        self.day_format = re.compile(r"^([0-9]{8}|[0-9/.-]{8,10})$")
        """日付文字列判定用正規表現
        - *yyyymmdd*
        - *yyyy/mm/dd*, *yyyy/m/d*
        - *yyyy-mm-dd*, *yyyy-m-d*
        - *yyyy.mm.dd*, *yyyy.m.d*
        """

    @classmethod
    def is_valid_command(cls, word: str) -> bool:
        """
        引数がコマンド名と一致するか判定する

        Args:
            word (str): チェック文字列

        Returns:
            bool: 真偽

        """
        for cmd in COMMANDS.values():
            for pattern in cmd["match"]:
                m = re.match(pattern, word)
                if m:
                    return True
                m = re.match(pattern, textutil.str_conv(word.lower(), textutil.ConversionType.HtoK))
                if m:
                    return True

        return False

    def analysis_argument(self, argument: list[str]) -> ParsedCommand:
        """
        コマンドライン引数を解析する

        Args:
            argument (list[str]): 引数

        Returns:
            ParsedCommand: 結果

        """
        ret: dict[str, Any] = {}
        unknown: list[str] = []
        args: list[str] = []
        search_range: list[Any] = []

        for keyword in argument:
            check_word = textutil.str_conv(keyword.lower(), textutil.ConversionType.HtoK)
            check_word = check_word.replace("無シ", "ナシ").replace("有リ", "アリ")

            if re.match(r"^([0-9]{8}|[0-9/.-]{8,10})$", check_word):
                try_day = pd.to_datetime(check_word, errors="coerce").to_pydatetime()
                if not pd.isna(try_day):
                    search_range.append(ExtDt(try_day))
                    search_range.append(ExtDt(try_day) + {"hour": 23, "minute": 59, "second": 59, "microsecond": 999999})
                continue

            if check_word in ExtDt.valid_keywords():
                search_range.append(check_word)
                continue

            for cmd in COMMANDS.values():
                for pattern in cmd["match"]:
                    m = re.match(pattern, keyword)
                    if m:
                        ret.update(self._parse_match(cmd, m))
                        break
                    m = re.match(pattern, check_word)
                    if m:
                        ret.update(self._parse_match(cmd, m))
                        break
                else:
                    continue
                break
            else:
                unknown.append(formatter.name_replace(keyword, add_mark=False, not_replace=True))

        return ParsedCommand(flags=ret, arguments=args, unknown=unknown, search_range=search_range)

    def _parse_match(self, cmd: CommandSpec, obj: re.Match) -> dict[str, Any]:
        """
        コマンド名に一致したときの処理

        Args:
            cmd (CommandSpec): コマンドマップ
            obj (re.Match): Matchオブジェクト

        Returns:
            dict[str, Any]: 更新用辞書

        """
        ret: dict[str, Any] = {}

        def with_arguments(tmp: dict[str, Any]) -> None:
            key = str(next(iter(tmp.keys())))
            val = str(tmp[key][1])
            if "" != val:
                match cmd.get("type"):
                    case "str":
                        ret.update({key: val})
                    case "sql":
                        ret.update({key: f"%{val}%"})
                    case "filename":
                        if re.search(r"^[\w\-\.]+$", val):
                            ret.update({key: val})
                    case "int":
                        ret.update({key: int(val)})
                    case _:
                        ret.update({key: int(val) if val.isdigit() else val})

        match len(obj.groups()):
            case 0:  # 完全一致: ^command$
                ret.update(cmd["action"](obj.group()))
            case 1:  # 選択: ^(command1|command2|...)$
                ret.update(cmd["action"](obj.groups()[0]))
            case 2:  # 引数あり: ^(command)(\d*)$
                tmp = cmd["action"](obj.groups())
                if isinstance(tmp, dict):
                    for k, v in tmp.items():
                        if isinstance(v, tuple):  # 引数取り出し&セット
                            with_arguments(tmp)
                        if isinstance(v, bool):  # フラグ上書き
                            ret.update({k: v})

        return ret


@dataclass
class PlaceholderBuild(ParameterData):
    """プレースホルダ構築クラス"""

    # ルール情報
    target_mode: int = field(default=0)
    """集計対象モードの指定
    - *0*: settingのデフォルトに従う
    - *not 0*: 指定値でmodeを上書き
    """
    mode: int = field(default=4)
    """集計モード"""
    default_rule: str = field(default="")
    """ルール識別子(設定値)"""
    rule_version: str = field(default="")
    """ルール識別子(指定値)"""
    rule_list: list[str] = field(default_factory=list)
    """集計対象ルール識別子"""
    mixed: bool = field(default=False)
    """ルール識別子の扱い
    - *True*: 定義済みすべてのルール識別子を含める
    - *False*: ルール識別子を個別指定
    """
    # ルールセット登録用
    origin_point: int = field(default=250)
    """配給原点"""
    return_point: int = field(default=300)
    """返し点"""
    rank_point: str = field(default="")
    """順位点(空白区切りの文字列)"""
    ignore_flying: bool = field(default=False)
    """トビカウントの無効化"""
    draw_split: bool = field(default=False)
    """同点時の順位点の取り扱い
    - *True*: 山分け
    - *False*: 席順
    """
    undefined_word: int = field(default=1)
    """未登録ワードの扱い
    - *0*: 役満扱い
    - *1*: カウントのみ
    - *2*: 卓外清算(個人清算)
    - *3*: 卓外清算(チーム清算)
    """

    # 集計対象情報
    player_name: str = field(default="")
    """集計対象プレイヤー"""
    guest_name: str = field(default="")
    """ゲストの名前"""
    target_player: list[str] = field(default_factory=list)
    """比較対象プレイヤーリスト"""
    player_list: list[str] = field(default_factory=list)
    """集計対象プレイヤーリスト"""
    competition_list: list[str] = field(default_factory=list)
    """比較対象プレイヤーリスト"""
    all_player: bool = field(default=False)
    """検索対象に登録済みメンバー全員を加える"""
    source: str = field(default="")
    """スコア入力元識別子"""
    separate: bool = field(default=False)
    """スコア入力元識別子別集計フラグ
    - *True*: 識別子別に集計
    - *False*: すべて集計
    """
    collection: str = field(default="")
    """集約集計
    - *daily*: 日次集約
    - *weekly*: 週次集約
    - *monthly*: 月次集約
    - *yearly*: 年次集約
    - *all*: 全体集約
    """
    target_count: int = field(default=0)
    """直近ゲーム数指定"""

    starttime: Union[str, ExtDt, None] = field(default=None)
    """集計開始日時"""
    endtime: Union[str, ExtDt, None] = field(default=None)
    """集計終了日時"""
    onday: Union[str, ExtDt, None] = field(default=None)
    """time_adjust修正を含まない日時"""

    # 動作/表示変更フラグ
    score_comparisons: bool = field(default=False)
    """スコア比較表示"""
    verbose: bool = field(default=False)
    """詳細情報表示"""
    game_results: bool = field(default=False)
    """ゲーム結果表示"""
    versus_matrix: bool = field(default=False)
    """対戦マトリックス表示"""
    anonymous: bool = field(default=False)
    """匿名化フラグ"""
    fourfold: bool = field(default=True)
    """縦持ち/横持ちデータ判定"""

    # 出力関連
    format: Literal["default", "csv", "txt"] = field(default="default")
    """出力フォーマット指定"""
    filename: str = field(default="")
    """出力ファイル名"""

    def update_to_dict(self, input_dict: dict[str, Any]) -> None:
        """
        辞書の内容で値を更新する

        Args:
            input_dict (dict[str,Any]): 更新内容

        """
        field_list: list[str] = [x.name for x in fields(self)]
        for k, v in input_dict.items():
            if k in field_list:
                setattr(self, k, v)

    def placeholder(self) -> dict[str, Any]:
        """プレースホルダ用辞書出力"""
        ret_dict: dict[str, Any] = asdict(self)

        if self.player_list:
            ret_dict.update({f"player_{idx}": x for idx, x in enumerate(self.player_list)})
        ret_dict.pop("player_list")

        if self.target_player:
            ret_dict.update({f"target_{idx}": x for idx, x in enumerate(self.target_player)})
        ret_dict.pop("target_player")

        if self.competition_list:
            ret_dict.update({f"competition_{idx}": x for idx, x in enumerate(self.competition_list)})
        ret_dict.pop("competition_list")

        if self.rule_list:
            ret_dict.update({f"rule_{idx}": x for idx, x in enumerate(self.rule_list)})
        else:
            ret_dict.update({"rule_0": self.rule_version})
        ret_dict.pop("rule_list")

        return ret_dict
