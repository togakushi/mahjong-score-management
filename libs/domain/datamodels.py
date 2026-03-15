"""
libs/domain/datamodels.py
"""

import logging
from dataclasses import MISSING, asdict, dataclass, field, fields
from enum import StrEnum
from math import ceil
from typing import TYPE_CHECKING, Any, Literal, Optional

import libs.global_value as g
from libs.data import loader
from libs.utils.timekit import ExtendedDatetime as ExtDt
from libs.utils.timekit import Format

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol
    from libs.domain.score import GameResult
    from libs.types import RemarkDict


class CommandType(StrEnum):
    """実行(する/した)サブコマンド"""

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


@dataclass
class GameInfo:
    """ゲーム集計情報"""

    count: int = field(default=0)
    """集計範囲のゲーム数"""
    first_game: Optional[ExtDt] = field(default=None)
    """集計範囲の最初のゲーム時間"""
    last_game: Optional[ExtDt] = field(default=None)
    """集計範囲の最後のゲーム時間"""
    first_comment: Optional[str] = field(default=None)
    """集計範囲の最初のゲームコメント"""
    last_comment: Optional[str] = field(default=None)
    """集計範囲の最後のゲームコメント"""

    def __post_init__(self) -> None:
        self.get()

    def get(self) -> None:
        """指定条件を満たすゲーム数のカウント、最初と最後の時刻とコメントを取得"""
        # グローバルパラメータチェック
        if "rule_version" not in g.params:
            g.params.update({"rule_version": g.cfg.setting.default_rule})
        if "starttime" not in g.params:
            g.params.update({"starttime": ExtDt().range("全部").start})
        if "endtime" not in g.params:
            g.params.update({"endtime": ExtDt().range("全部").end})

        # データ収集
        df = loader.read_data("GAME_INFO", g.params)
        if df.empty:
            self.count = 0
            self.first_game = ExtDt()
            self.last_game = ExtDt()
            self.first_comment = ""
            self.last_comment = ""
        else:
            self.count = int(df["count"].iloc[0])
            self.first_game = ExtDt(str(df["first_game"].iloc[0]))
            self.last_game = ExtDt(str(df["last_game"].iloc[0]))
            self.first_comment = str(df["first_comment"].iloc[0])
            self.last_comment = str(df["last_comment"].iloc[0])

        # 規定打数更新
        if not g.params.get("stipulated", 0):  # 規定打数0はレートから計算
            match g.params.get("command", ""):
                case "results":
                    g.params["stipulated"] = g.cfg.results.stipulated_calculation(self.count)
                case "graph":
                    g.params["stipulated"] = g.cfg.graph.stipulated_calculation(self.count)
                case "ranking":
                    g.params["stipulated"] = g.cfg.ranking.stipulated_calculation(self.count)
                case "report":
                    g.params["stipulated"] = g.cfg.report.stipulated_calculation(self.count)
                case _:
                    pass

        logging.debug(self)

    def clear(self) -> None:
        """情報削除"""
        self.count = 0
        self.first_game = None
        self.first_comment = None
        self.last_game = None
        self.last_comment = None

    def conditions(self) -> dict[str, str | ExtDt | None]:
        """検索条件を返す"""
        return {
            "rule_version": g.params.get("rule_version"),
            "starttime": g.params.get("starttime"),
            "endtime": g.params.get("endtime"),
        }


@dataclass
class ComparisonResults:
    """突合結果"""

    search_after: int = field(default=-7)
    """突合範囲(日数)"""
    score_list: dict[str, "MessageParserProtocol"] = field(default_factory=dict)
    """スコアリスト(一時保管用)"""

    mismatch: list[dict[str, "GameResult"]] = field(default_factory=list)
    """スコア差分"""
    missing: list["GameResult"] = field(default_factory=list)
    """スコア追加"""
    delete: list["GameResult"] = field(default_factory=list)
    """スコア削除"""
    remark_mod: list["RemarkDict"] = field(default_factory=list)
    """メモ変更"""
    remark_del: list["RemarkDict"] = field(default_factory=list)
    """メモ削除"""
    invalid_score: list["GameResult"] = field(default_factory=list)
    """素点合計不一致"""
    pending: list["GameResult"] = field(default_factory=list)
    """処理保留データ"""

    @property
    def after(self) -> ExtDt:
        """突合開始日時"""
        return ExtDt(days=self.search_after, hours=g.cfg.setting.time_adjust)

    @property
    def before(self) -> ExtDt:
        """突合終了日時"""
        return ExtDt()

    def output(
        self,
        kind: Literal[
            "summary",
            "headline",
            "pending",
            "mismatch",
            "missing",
            "delete",
            "remark_mod",
            "remark_del",
            "invalid_score",
        ],
    ) -> str:
        """
        出力メッセージ生成

        Args:
            kind (Literal[summary, headline, pending, mismatch, missing, delete, remark_mod, remark_del, invalid_score]): 種類

        Returns:
            str: 生成文字列

        """  # noqa: E501
        ret: str = ""
        match kind:
            case "summary":
                ret += f"pending:{len(self.pending)} "
                ret += f"mismatch:{len(self.mismatch)} "
                ret += f"missing:{len(self.missing)} "
                ret += f"delete:{len(self.delete)} "
                ret += f"remark_mod:{len(self.remark_mod)} "
                ret += f"remark_del:{len(self.remark_del)} "
                ret += f"invalid_score:{len(self.invalid_score)} "
            case "headline":
                ret = f"突合範囲：{self.after.format(Format.YMDHMS)} - {self.before.format(Format.YMDHMS)}"
            case "pending":
                ret += f"＊ 保留：{len(self.pending)}件\n"
                for score in self.pending:
                    ret += f"{ExtDt(float(score.ts)).format(Format.YMDHMS)} {score.to_text()}\n"
            case "mismatch":
                ret += f"＊ 不一致：{len(self.mismatch)}件\n"
                for score_dict in self.mismatch:
                    ret += f"{ExtDt(float(score_dict['before'].ts)).format(Format.YMDHMS)}\n"
                    ret += f"\t修正前：{score_dict['before'].to_text()}\n"
                    ret += f"\t修正後：{score_dict['after'].to_text()}\n"
            case "missing":
                ret += f"＊ 取りこぼし：{len(self.missing)}件\n"
                for score in self.missing:
                    ret += f"{ExtDt(float(score.ts)).format(Format.YMDHMS)} {score.to_text()}\n"
            case "delete":
                ret += f"＊ 削除漏れ：{len(self.delete)}件\n"
                for score in self.delete:
                    ret += f"{ExtDt(float(score.ts)).format(Format.YMDHMS)} {score.to_text()}\n"
            case "remark_mod":
                ret += f"＊ メモ更新：{len(self.remark_mod)}件\n"
                for remark in self.remark_mod:
                    ret += f"{ExtDt(float(remark['thread_ts'])).format(Format.YMDHMS)} "
                    ret += f"{remark['name']} {remark['matter']}\n"
            case "remark_del":
                ret += f"＊ メモ削除：{len(self.remark_del)}件\n"
            case "invalid_score":
                ret += f"＊ 素点合計不一致：{len(self.invalid_score)}件\n"
                for score in self.invalid_score:
                    ret += f"{ExtDt(float(score.ts)).format(Format.YMDHMS)} {score.to_text()}\n"

        return ret


@dataclass
class ParameterData:
    """動作パラメータ"""

    # 検索条件変更フラグ
    individual: bool = field(default=True)
    """個人/チーム集計切替フラグ
    - *True*: 個人集計
    - *False*: チーム集計
    """
    guest_skip: bool = field(default=True)
    """ゲストアリ/ナシフラグ(サマリ集計用)"""
    guest_skip2: bool = field(default=True)
    """ゲストアリ/ナシフラグ(詳細集計用)"""
    unregistered_replace: bool = field(default=True)
    """メンバー未登録プレイヤー名をゲストに置き換えるかフラグ
    - *True*: 置き換える
    - *False*: 置き換えない
    """
    friendly_fire: bool = field(default=False)
    """チーム戦集計時のチーム同卓ゲームの扱い
    - *True*: チーム同卓ゲームを集計(同じチームのポイントは合算される)
    - *False*: チーム同卓ゲームを集計対象外にする
    """

    # 動作変更フラグ
    statistics: bool = field(default=False)
    """統計情報表示"""

    # 表示情報変更フラグ
    ranked: int = field(default=3)
    """ランキング/レーティングで表示する順位"""
    stipulated: int = field(default=0)
    """規定打数指定"""
    stipulated_rate: float = field(default=0.05)
    """規定打数計算レート"""

    # 集約条件変更フラグ
    interval: int = field(default=80)
    """移動平均算出ゲーム数指定"""

    # コメント検索
    search_word: str = field(default="")
    """コメント検索文字列"""
    group_length: int = field(default=0)
    """コメント検索時に指定文字数でグループ化する"""

    def default_reset(self) -> None:
        """デフォルト値にリセット"""
        for f in fields(self):
            if f.default is not MISSING:
                setattr(self, f.name, f.default)
            elif f.default_factory is not MISSING:
                setattr(self, f.name, f.default_factory())

    def stipulated_update(self, game_count: int) -> None:
        """
        ゲーム数から規定打数を再計算

        Args:
            game_count (int): 指定ゲーム数

        """
        self.stipulated = int(ceil(game_count * self.stipulated_rate) + 1)

    def dict_dump(self) -> dict[str, Any]:
        """dump to dict"""
        return asdict(self)


@dataclass
class CommandAttrs(ParameterData):
    """サブコマンド設定パラメータ"""

    commandword: list[str] = field(default_factory=list)
    """呼び出しキーワード"""
    command_suffix: list[str] = field(default_factory=list)
    """コマンド接尾辞(登録キーワード+接尾辞を呼び出しキーワードとして扱う)"""

    aggregation_range: str = field(default="当日")
    """検索範囲未指定時に使用される範囲"""
    always_argument: list[str] = field(default_factory=list)
    """オプションとして常に付与される文字列"""
    dropitems: list[str] = field(default_factory=list)
    """非表示にする項目"""

    def stipulated_calculation(self, game_count: int) -> int:
        """
        規定打数をゲーム数から計算

        Args:
            game_count (int): 指定ゲーム数

        Returns:
            int: 規定ゲーム数

        """
        return int(ceil(game_count * self.stipulated_rate) + 1)
