"""
libs/types.py
"""

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from enum import Enum, StrEnum, auto
from typing import TYPE_CHECKING, Any, Literal, Optional, TypeAlias, TypedDict, Union

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from integrations.protocols import MessageParserProtocol


MessageType: TypeAlias = Union[None, str, "Path", "pd.DataFrame"]
"""メッセージ型
- *None*: 空データ(なにもしない)
- *str*: 文字列型データ(そのまま表示)
- *Path*: ファイルパス(アップロード処理)
- *DataFrame*: 表データ
"""


class MessageStatus(StrEnum):
    """メッセージステータス"""

    APPEND = "message_append"
    """新規ポストイベント"""
    CHANGED = "message_changed"
    """編集イベント"""
    DELETED = "message_deleted"
    """削除イベント"""
    DO_NOTHING = "do_nothing"
    """何もしなくてよいイベント"""
    UNDETERMINED = "undetermined"
    """未定義状態"""


class ActionStatus(StrEnum):
    """DBに対する操作"""

    CHANGE = "change"
    """insert/updateが実行された"""
    DELETE = "delete"
    """deleteが実行された"""
    NOTHING = "nothing"
    """何もしてない"""


class ChannelType(StrEnum):
    """チャンネルタイプ"""

    CHANNEL = "normal"
    """通常チャンネル"""
    PRIVATE = "private"
    """プライベートチャンネル"""
    DIRECT_MESSAGE = "direct_message"
    """ダイレクトメッセージ"""
    HOME_APP = "home_app"
    """Slackのホームアプリ"""
    SEARCH = "search_api"
    """検索API"""
    UNDETERMINED = "undetermined"
    """未定義状態"""


class CommandType(StrEnum):
    """実行(する/した)コマンド名"""

    # 集計コマンド
    RECORD_DATA = "成績データ"
    """集計コマンド: 成績詳細 / 成績グラフ"""
    RECORD_SUMMARY = "成績サマリ"
    """集計コマンド: 成績サマリ表(全体/差分) / 成績上位者"""
    RECORD_GRAPH = "成績グラフ"
    """集計コマンド: 通算ポイント推移グラフ / 順位変動グラフ"""
    GAME_RESULTS = "対戦結果"
    """集計コマンド: 直接対戦結果"""

    # 分析コマンド
    RANKING = "ランキング"
    """分析コマンド: ランキング"""
    RATING = "レーティング"
    """分析コマンド: レーティング表 / レーティング推移グラフ"""
    MATRIX = "マトリクス"
    """分析コマンド: 対局対戦マトリクス"""
    GAME_STATISTICS = "ゲーム統計"
    """分析コマンド: ゲーム統計情報"""
    ANALYSIS_SCORES = "素点分析"
    """分析コマンド: 素点分析 / 順位素点相関図"""
    DETAILED_RESULTS = "成績詳細"
    """分析コマンド: 成績レポート / 成績分析 / 成績詳細一覧表"""

    # その他
    HELP = "help"
    """その他コマンド: ヘルプ"""
    MEMBERS_LIST = "メンバー一覧"
    """その他コマンド: メンバー一覧"""
    TEAM_LIST = "チーム一覧"
    """その他コマンド: チーム一覧"""
    COMPARISON = "突合"
    """突合処理"""
    UNKNOWN = "未定義"
    """未定義"""


class ServiceType(StrEnum):
    """連携先サービス"""

    SLACK = "slack"
    """slack"""
    DISCORD = "discord"
    """discord"""
    WEB = "web"
    """web ui"""
    STANDARD_IO = "standard_io"
    """standard_io"""
    UNKNOWN = "unknown"
    """unknown"""


@dataclass
class StyleOptions:
    """表示オプション"""

    class RenameType(Enum):
        """リネームタイプ"""

        NONE = auto()
        """変換しない"""
        NORMAL = auto()
        """通常変換"""
        SHORT = auto()
        """短縮変換"""

    class DataKind(Enum):
        """保存されているデータの種類"""

        GENERAL = auto()
        """通常データ"""
        POINTS_TOTAL = auto()
        """成績サマリ(通算ポイント)"""
        POINTS_DIFF = auto()
        """成績サマリ(ポイント差分)"""
        SCORE_ANALYSIS = auto()
        """成績サマリ(素点分析)"""
        STATS_LIST = auto()
        """成績詳細一覧"""
        SEAT_DATA = auto()
        """座席データ"""
        RECORD_DATA = auto()
        """戦績データ(簡易版)"""
        RECORD_DATA_ALL = auto()
        """戦績データ(詳細版)"""
        RANKING = auto()
        """ランキングデータ"""
        RATING = auto()
        """レーティングデータ"""
        GAME_STATISTICS = auto()
        """ゲーム統計表"""

        # メモ
        REMARKS_REGULATION = auto()
        """メモ(卓外清算)"""
        REMARKS_YAKUMAN = auto()
        """メモ(役満和了)"""
        REMARKS_OTHER = auto()
        """メモ(その他)"""

    title: str = ""
    """出力タイトル"""
    sub_title: bool = False
    """サブタイトル化"""
    format_type: Literal["default", "csv", "txt"] = "default"
    """出力フォーマット"""

    base_name: str = ""
    """ファイル出力時のファイル名"""

    codeblock: bool = False
    """MessageTypeがstr型ならcodeblock化
    - *True*: codeblock化
    - *False*: 何もしない
    """
    show_index: bool = False
    """MessageTypeがDataFrame型なら表にIndexに含める
    - *True*: Indexを含める
    - *False*: Indexを含めない
    """
    use_comment: bool = False
    """ファイルアップロード時のinitial_commentを有効にする
    - *True*: initial_commentを使う
    - *False*: initial_commentを使わない
    """
    header_hidden: bool = False
    """ヘッダ文を非表示にする
    - *True*: 非表示
    - *False*: 表示
    """
    key_title: bool = True
    """小見出しに辞書のキーを使う
    - *True*: 表示
    - *False*: 非表示
    """
    summarize: bool = True
    """MessageTypeがstr型のとき後続の要素を集約する
    - *True*: 可能な限り複数の要素をひとつにまとめる
    - *False*: 要素単位でデータを処理する
    """
    indent: int = 0
    """出力時に付与するインデント数(TAB)"""
    keep_blank: bool = False
    """空行の削除
    - *True*: 削除しない
    - *False*: 削除する
    """
    keep_indent: bool = False
    """保存されているメッセージのdedentの取り扱い
    - *True*: 維持する
    - *False*: 削除する
    """
    transpose: bool = False
    """MessageTypeがDataFrameのとき表の縦横を変換する"""
    rename_type: RenameType = field(default=RenameType.NORMAL)
    """カラム名変換パラメータ"""
    data_kind: DataKind = field(default=DataKind.GENERAL)
    """データ種別"""

    @property
    def print_title(self) -> str:
        """
        タイトル表示

        Returns:
            str: タイトル文字列

        """
        ret: str = ""

        if self.title:
            tab = "\t" * (self.indent - 1)
            if self.sub_title:
                ret = f"{tab}{self.title}："
            else:
                ret = f"{tab}【{self.title}】"

        return ret

    @property
    def filename(self) -> str:
        """出力ファイル名"""
        if self.format_type == "default":
            return ""
        return f"{self.base_name}.{self.format_type}"

    @property
    def asdict(self) -> dict[str, Any]:
        """辞書変換"""
        return asdict(self)


@dataclass(frozen=True)
class DispatchRule:
    """コマンドディスパッチルールテーブル"""

    name: str
    """コマンド名"""
    condition: Callable[[], bool]
    """オプション状態"""
    handler: Callable[["MessageParserProtocol"], None]
    """実行関数"""


class MessageTypeDict(TypedDict):
    """メッセージ格納辞書"""

    data: MessageType
    """内容"""
    options: StyleOptions
    """表示オプション"""


class ScoreDict(TypedDict, total=False):
    """スコアデータ格納用辞書"""

    ts: str
    """ゲーム終了時間"""

    p1_name: str
    """東家：プレイヤー名"""
    p1_str: str
    """東家：入力された素点情報(文字列)"""
    p1_rpoint: int
    """東家：素点(入力文字列評価後)"""
    p1_point: float
    """東家：獲得ポイント"""
    p1_rank: int
    """東家：獲得順位"""

    p2_name: str
    """南家：プレイヤー名"""
    p2_str: str
    """南家：入力された素点情報(文字列)"""
    p2_rpoint: int
    """南家：素点(入力文字列評価後)"""
    p2_point: float
    """東家：獲得ポイント"""
    p2_rank: int
    """南家：獲得順位"""

    p3_name: str
    """西家：プレイヤー名"""
    p3_str: str
    """西家：入力された素点情報(文字列)"""
    p3_rpoint: int
    """西家：素点(入力文字列評価後)"""
    p3_point: float
    """西家：獲得ポイント"""
    p3_rank: int
    """西家：獲得順位"""

    p4_name: str
    """北家：プレイヤー名"""
    p4_str: str
    """北家：入力された素点情報(文字列)"""
    p4_rpoint: int
    """北家：素点(入力文字列評価後)"""
    p4_point: float
    """北家：獲得ポイント"""
    p4_rank: int
    """北家：獲得順位"""

    deposit: int
    """配給原点合計 - 素点合計"""
    comment: Optional[str]
    """ゲームコメント"""
    rule_version: str
    """ルール識別子"""
    source: Optional[str]
    """データ入力元識別子"""
    mode: Literal[3, 4]
    """集計モード"""


class RemarkDict(TypedDict, total=False):
    """メモ格納用辞書"""

    thread_ts: str
    """ゲーム終了時間"""
    event_ts: str
    """メモ記録時間"""
    name: str
    """記録対象プレイヤー名"""
    matter: str
    """記録内容"""
    source: str
    """データ入力元識別子"""


class RankTableDict(TypedDict):
    """昇段ポイント計算テーブル用辞書"""

    grade: str
    """段位名称"""
    point: list[int]
    """初期ポイントと昇段に必要なポイント"""
    acquisition: list[int]
    """獲得ポイント(順位)"""
    demote: bool
    """降格フラグ
    - *True*: 降格する(省略時デフォルト)
    - *False*: 降格しない
    """


class GradeTableDict(TypedDict, total=False):
    """段位テーブル用辞書"""

    name: str
    """識別名"""
    addition_expression: str
    """素点評価式(昇段ポイントに加算)"""
    table: list[RankTableDict]
    """昇段ポイント計算テーブル"""
