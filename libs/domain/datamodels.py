"""
libs/domain/datamodels.py
"""

import logging
from dataclasses import MISSING, dataclass, field, fields
from math import ceil
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import pandas as pd

import libs.global_value as g
from libs.domain.stats import StatsInfo
from libs.functions import lookup
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from pathlib import Path

    from integrations.protocols import MessageParserProtocol
    from libs.domain.score import GameResult
    from libs.types import RemarkDict


@dataclass
class Args:
    """コマンドラインオプション"""

    service: str
    config: "Path"
    """設定ファイルパス"""
    no_cleanup: bool
    """作業ディレクトリの内容を削除"""

    debug: int
    """デバッグ出力フラグ"""
    verbose: int
    """詳細出力フラグ"""

    moderate: bool
    """INFO以下のログレベル出力を抑止"""
    notime: bool
    """ログに日付を付与しない"""

    # Only allowed when --service=standard_io
    text: str

    # Only allowed when --service=web
    host: str
    port: int

    # dbtools
    compar: bool
    unification: "Path"
    recalculation: list[str]
    export_data: str
    import_data: str
    vacuum: bool
    gen_test_data: int
    testcase: Optional["Path"]


@dataclass
class GameInfo:
    """ゲーム集計情報"""

    starttime: Union[str, ExtDt, None] = field(default=None)
    """検索開始日時"""
    endtime: Union[str, ExtDt, None] = field(default=None)
    """検索終了日時"""
    count: int = field(default=0)
    """集計範囲の対戦数"""
    first_game: Optional[ExtDt] = field(default=None)
    """集計範囲の最初のゲーム時間"""
    last_game: Optional[ExtDt] = field(default=None)
    """集計範囲の最後のゲーム時間"""
    first_comment: Optional[str] = field(default=None)
    """集計範囲の最初のゲームコメント"""
    last_comment: Optional[str] = field(default=None)
    """集計範囲の最後のゲームコメント"""
    rule_version: str = field(default="")
    """集計対象ルール識別子"""
    stats: StatsInfo = field(default_factory=StatsInfo)
    """個人/チーム集計時の成績情報"""

    def __post_init__(self) -> None:
        self.get()

    def get(self) -> None:
        """指定条件を満たす対戦数のカウント、最初と最後の時刻とコメントを取得"""
        # グローバルパラメータチェック
        if not g.params.rule_version:
            if g.cfg.setting.default_rule:
                g.params.rule_version = g.cfg.setting.default_rule
            else:
                g.params.rule_version = g.params.default_rule
        if not g.params.starttime:
            g.params.starttime = ExtDt().range("全部").start
        if not g.params.endtime:
            g.params.endtime = ExtDt().range("全部").end

        # データ収集
        self.rule_version = g.params.rule_version
        self.starttime = g.params.starttime
        self.endtime = g.params.endtime
        df = g.params.read_data("GAME_INFO")
        if df.empty:
            self.count = 0
            self.first_game = ExtDt()
            self.last_game = ExtDt()
            self.first_comment = None
            self.last_comment = None
        else:
            self.count = int(df["count"].iloc[0])
            self.first_game = ExtDt(str(df["first_game"].iloc[0]))
            self.last_game = ExtDt(str(df["last_game"].iloc[0]))
            first_comment_val = df["first_comment"].iloc[0]
            self.first_comment = str(first_comment_val) if pd.notna(first_comment_val) else None
            last_comment_val = df["last_comment"].iloc[0]
            self.last_comment = str(last_comment_val) if pd.notna(last_comment_val) else None

        # 規定打数更新
        if not g.params.stipulated:  # 規定打数0はレートから計算
            match g.params.command:
                case "summary":
                    g.params.stipulated = g.cfg.summary.stipulated_calculation(self.count)
                case "analysis":
                    g.params.stipulated = g.cfg.analysis.stipulated_calculation(self.count)
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

    @property
    def aggregation_range(self) -> str:
        """
        集計範囲を返す

        Returns:
            str: YYYY/MM/DD HH:MM:SS ～ YYYY/MM/DD HH:MM:SS

        """
        if g.params.search_word:  # コメント検索の場合はコメントで表示
            return f"{self.first_comment} ～ {self.last_comment}"
        else:
            assert isinstance(self.first_game, ExtDt)
            assert isinstance(self.last_game, ExtDt)
            return f"{self.first_game.format(ExtDt.FMT.YMDHMS)} ～ {self.last_game.format(ExtDt.FMT.YMDHMS)}"

    @property
    def search_range(self) -> str:
        """
        検索範囲を返す

        Returns:
            str: YYYY/MM/DD HH:MM:SS ～ YYYY/MM/DD HH:MM:SS

        """
        return f"{self.search_start} ～ {self.search_end}"

    @property
    def search_start(self) -> str:
        """
        検索開始日時を文字列で返す

        Returns:
            str: YYYY/MM/DD HH:MM:SS

        """
        assert isinstance(self.starttime, ExtDt)
        return self.starttime.format(fmt=ExtDt.FMT.YMDHMS)

    @property
    def search_end(self) -> str:
        """
        検索終了日時を文字列で返す

        Returns:
            str: YYYY/MM/DD HH:MM:SS

        """
        assert isinstance(self.endtime, ExtDt)
        return self.endtime.format(fmt=ExtDt.FMT.YMDHMS)


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
                ret = f"突合範囲：{self.after.format(ExtDt.FMT.YMDHMS)} - {self.before.format(ExtDt.FMT.YMDHMS)}"
            case "pending":
                ret += f"＊ 保留：{len(self.pending)}件\n"
                for score in self.pending:
                    ret += f"{ExtDt(float(score.ts)).format(ExtDt.FMT.YMDHMS)} {score.to_text()}\n"
            case "mismatch":
                ret += f"＊ 不一致：{len(self.mismatch)}件\n"
                for score_dict in self.mismatch:
                    ret += f"{ExtDt(float(score_dict['before'].ts)).format(ExtDt.FMT.YMDHMS)}\n"
                    ret += f"\t修正前：{score_dict['before'].to_text()}\n"
                    ret += f"\t修正後：{score_dict['after'].to_text()}\n"
            case "missing":
                ret += f"＊ 取りこぼし：{len(self.missing)}件\n"
                for score in self.missing:
                    ret += f"{ExtDt(float(score.ts)).format(ExtDt.FMT.YMDHMS)} {score.to_text()}\n"
            case "delete":
                ret += f"＊ 削除漏れ：{len(self.delete)}件\n"
                for score in self.delete:
                    ret += f"{ExtDt(float(score.ts)).format(ExtDt.FMT.YMDHMS)} {score.to_text()}\n"
            case "remark_mod":
                ret += f"＊ メモ更新：{len(self.remark_mod)}件\n"
                for remark in self.remark_mod:
                    ret += f"{ExtDt(float(remark['thread_ts'])).format(ExtDt.FMT.YMDHMS)} "
                    ret += f"{remark['name']} {remark['matter']}\n"
            case "remark_del":
                ret += f"＊ メモ削除：{len(self.remark_del)}件\n"
            case "invalid_score":
                ret += f"＊ 素点合計不一致：{len(self.invalid_score)}件\n"
                for score in self.invalid_score:
                    ret += f"{ExtDt(float(score.ts)).format(ExtDt.FMT.YMDHMS)} {score.to_text()}\n"

        return ret


@dataclass
class ParameterMethodMixin:
    """パラメータに関する共通的な取得メソッドを提供するMixin"""

    def default_reset(self) -> None:
        """デフォルト値にリセット"""
        for f in fields(self):
            if f.default is not MISSING:
                setattr(self, f.name, f.default)
            elif f.default_factory is not MISSING:
                setattr(self, f.name, f.default_factory())

    def get_default(self, key: str) -> Any:
        """
        フィールドのデフォルト値を取得

        Args:
            key (str): フィールド名

        Returns:
            Any: デフォルト値、またはNone
        """
        field_map = {f.name: f for f in fields(self)}
        f = field_map.get(key)
        if f is None:
            return None
        if f.default is not MISSING:
            return f.default
        if f.default_factory is not MISSING:
            return f.default_factory()
        return None


@dataclass
class ParameterData(ParameterMethodMixin):
    """コマンド動作パラメータ"""

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
    """移動平均を算出する対戦数の指定"""

    # コメント検索
    search_word: str = field(default="")
    """コメント検索文字列"""
    group_length: int = field(default=0)
    """コメント検索時に指定文字数でグループ化する"""


@dataclass
class SettingAttrs(ParameterMethodMixin):
    """コマンド設定基本パラメータ"""

    command_name: str
    """コマンド名"""
    default_commandword: str
    """コマンドワードデフォルト値"""
    commandword: list[str] = field(default_factory=list)
    """呼び出しキーワード"""
    command_suffix: list[str] = field(default_factory=list)
    """コマンド接尾辞(登録キーワード+接尾辞を呼び出しキーワードとして扱う)"""
    dropitems: list[str] = field(default_factory=list)
    """非表示にする項目"""

    @property
    def commandwords_list(self) -> list[str]:
        """
        コマンドリストを返す

        Returns:
            list: コマンドリスト

        """
        word_list: list[str] = []
        if not any([self.commandword, self.command_suffix]):  # 何も設定されていない
            word_list.append(self.default_commandword)
        elif self.commandword:
            word_list.extend(self.commandword)
        elif self.command_suffix:  # コマンドサフィックス登録
            for rule_version in g.cfg.rule.rule_list:
                word_list.extend(
                    [f"{prefix}{suffix}" for prefix in g.cfg.rule.keywords(rule_version) for suffix in self.command_suffix],
                )

        return word_list

    def help_string(self, section: str) -> str:
        """
        コマンドヘルプメッセージを生成する

        Args:
            section (str): コマンド種別（セクション名）

        Returns:
            str: ヘルプメッセージ
        """
        text_list: list[str] = []
        word_list: list[str] = lookup.resolve_commands(g.params.rule_version, section)

        text_list.append(f"呼び出しワード：{'、'.join(word_list)}")
        if hasattr(self, "aggregation_range"):
            text_list.append(f"検索範囲デフォルト：{self.aggregation_range}")
        if hasattr(self, "stipulated") and hasattr(self, "stipulated_rate") and not self.stipulated:
            text_list.append(f"規定打数デフォルト：総対戦数 × {self.stipulated_rate} ＋ 1")
        if hasattr(self, "ranked") and (self.ranked != self.get_default("ranked")):
            text_list.append(f"出力制限デフォルト：上位 {self.ranked} 名")

        return "\n".join(text_list)


@dataclass
class CommandAttrs(ParameterData, SettingAttrs):
    """コマンド設定追加パラメータ"""

    aggregation_range: str = field(default="当日")
    """検索範囲未指定時に使用される範囲"""
    always_argument: list[str] = field(default_factory=list)
    """オプションとして常に付与される文字列"""

    def stipulated_calculation(self, game_count: int) -> int:
        """
        規定打数を対戦数から計算

        Args:
            game_count (int): 指定対戦数

        Returns:
            int: 規定対戦数

        """
        return int(ceil(game_count * self.stipulated_rate) + 1)
