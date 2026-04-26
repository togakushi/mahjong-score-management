"""
libs/types.py
"""

from dataclasses import asdict, dataclass, field
from enum import Enum, StrEnum, auto
from typing import TYPE_CHECKING, Any, Literal, Optional, TypeAlias, TypedDict, Union

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd


MessageType: TypeAlias = Union[None, str, "Path", "pd.DataFrame"]
"""メッセージ型
- *None*: 空データ(なにもしない)
- *str*: 文字列型データ(そのまま表示)
- *Path*: ファイルパス(アップロード処理)
- *DataFrame*: 表データ
"""

RENAME_DICT: dict[str, str] = {
    #
    "p1": "東家",
    "p2": "南家",
    "p3": "西家",
    "p4": "北家",
    "alias": "別名",
    "members": "所属メンバー",
    "last_update": "最終更新日",
    "elapsed_day": "経過日数",
    #
    "playtime": "日時",
    "rate": "レート",
    "participation_rate": "ゲーム参加率",
    "total_count": "集計ゲーム数",
    "matter_count": "回数",
    "ex_total": "ポイント合計",
    "deposit": "供託",
    "comment": "コメント",
    "source": "入力元",
    "rule_version": "ルール識別子",
    "war_record": "戦績(勝-敗-分)",
    #
    "rpoint": "素点",
    "rpoint_avg": "平均素点",
    "balance_avg": "平均収支",
    "point_dev": "得点偏差",
    "rank_dev": "順位偏差",
    "grade": "段位",
    #
    "rank1_rate-count": "1位率(回)",
    "rank1_rate": "1位率",
    "rank2_rate-count": "2位率(回)",
    "rank2_rate": "2位率",
    "rank3_rate-count": "3位率(回)",
    "rank3_rate": "3位率",
    "rank4_rate-count": "4位率(回)",
    "rank4_rate": "4位率",
    "top2_rate-count": "連対率(回)",
    "top2_rate": "連対率",
    "top2": "連対数",
    "top3_rate-count": "ラス回避率(回)",
    "top3_rate": "ラス回避率",
    "top3": "ラス回避数",
    "flying_rate-count": "トビ率(回)",
    "flying_rate": "トビ率",
    "flying_count": "トビ数",
    "yakuman_rate-count": "役満和了率(回)",
    # 収支
    "avg_balance": "平均収支",
    "top2_balance": "連対収支",
    "lose2_balance": "逆連対収支",
    "rank1_balance": "1位収支",
    "rank2_balance": "2位収支",
    "rank3_balance": "3位収支",
    "rank4_balance": "4位収支",
    # レコード
    "top1_max": "連続トップ",
    "top2_max": "連続連対",
    "top3_max": "連続ラス回避",
    "lose2_max": "連続トップなし",
    "lose3_max": "連続逆連対",
    "lose4_max": "連続ラス",
    "point_max": "最大獲得ポイント",
    "point_min": "最小獲得ポイント",
    "rpoint_max": "最大素点",
    "rpoint_min": "最小素点",
    # 直接対決
    "results": "対戦結果",
    "win%": "勝率",
    "my_point_sum": "獲得ポイント(自分)",
    "my_point_avg": "平均ポイント(自分)",
    "vs_point_sum": "獲得ポイント(相手)",
    "vs_point_avg": "平均ポイント(相手)",
    "my_rpoint_avg": "平均素点(自分)",
    "my_rank_avg": "平均順位(自分)",
    "my_rank_distr": "順位分布(自分)",
    "vs_rpoint_avg": "平均素点(相手)",
    "vs_rank_avg": "平均順位(相手)",
    "vs_rank_distr": "順位分布(相手)",
    #
    "p1_name": "東家 名前",
    "p2_name": "南家 名前",
    "p3_name": "西家 名前",
    "p4_name": "北家 名前",
    "p1_yakuman": "東家 メモ",
    "p2_yakuman": "南家 メモ",
    "p3_yakuman": "西家 メモ",
    "p4_yakuman": "北家 メモ",
    "p1_remarks": "東家 メモ",
    "p2_remarks": "南家 メモ",
    "p3_remarks": "西家 メモ",
    "p4_remarks": "北家 メモ",
    "p1_rpoint": "東家 素点",
    "p2_rpoint": "南家 素点",
    "p3_rpoint": "西家 素点",
    "p4_rpoint": "北家 素点",
    "p1_rank": "東家 順位",
    "p2_rank": "南家 順位",
    "p3_rank": "西家 順位",
    "p4_rank": "北家 順位",
    "p1_point": "東家 ポイント",
    "p2_point": "南家 ポイント",
    "p3_point": "西家 ポイント",
    "p4_point": "北家 ポイント",
    "p1_str": "東家 入力素点",
    "p2_str": "南家 入力素点",
    "p3_str": "西家 入力素点",
    "p4_str": "北家 入力素点",
    # レポート - 上位成績
    "collection": "集計月",
    "name1": "1位(名前)",
    "point1": "1位(ポイント)",
    "name2": "2位(名前)",
    "point2": "2位(ポイント)",
    "name3": "3位(名前)",
    "point3": "3位(ポイント)",
    "name4": "4位(名前)",
    "point4": "4位(ポイント)",
    "name5": "5位(名前)",
    "point5": "5位(ポイント)",
    # メモ
    "regulation": "卓外清算",
    "remarks": "メモ",
    #
    "memo": "備考",
}


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
    """実行(する/した)サブコマンド兼設定ファイルセクション名"""

    RESULTS = "results"
    """成績サマリ"""
    GRAPH = "graph"
    """グラフ生成"""
    RANKING = "ranking"
    """ランキング"""
    RATING = "rating"
    """レーティング"""
    REPORT = "report"
    """レポート"""
    MEMBER_LIST = "member"
    """メンバー一覧"""
    TEAM_LIST = "team"
    """チーム一覧"""
    HELP = "help"
    """ヘルプ"""
    COMPARISON = "comparison"
    """突合処理"""
    UNKNOWN = "unknown"
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
        DETAILED_COMPARISON = auto()
        """成績詳細比較"""
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
