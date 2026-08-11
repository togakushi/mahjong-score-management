"""
libs/domain/score.py
"""

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Optional, cast

import pandas as pd

if TYPE_CHECKING:
    from libs.types import ScoreDict


@dataclass
class Score:
    """
    プレイヤー個人の成績データを保持するクラス

    Note:
        ``r_str`` の ``r_`` プレフィックスは、 GameResult.to_dict() によって
        ``p1_``, ``p2_``, ``p3_``, ``p4_`` に置換され、
        DBテーブルのカラム名 ( ``p1_str``, ``p2_str`` など) として使用する。

    """

    name: str = field(default="")
    """プレイヤー名"""
    r_str: str = field(default="")
    """素点(ユーザー入力文字列/未計算)"""
    rpoint: int = field(default=0)
    """素点(ユーザー入力文字列評価後)"""
    point: float = field(default=0.0)
    """獲得ポイント"""
    rank: float = field(default=0)
    """獲得順位"""

    def has_valid_data(self) -> bool:
        """
        有効なデータを持っているかチェック

        Returns:
            bool:
                - *True*: データ格納済み
                - *False*: 初期状態（空）

        """
        return self != Score()

    def to_dict(self, prefix: str) -> "ScoreDict":
        """
        データを辞書で返す

        Args:
            prefix (str): キーに付与する接頭辞 (``p1``, ``p2``, ``p3``, ``p4``)

        Returns:
            ScoreDict: 返却する辞書

        Note:
            フィールド名の ``r_`` プレフィックスは、指定された prefix に置換される。
            例: r_str -> p1_str (`prefix="p1"` の場合)

        """
        return cast(
            "ScoreDict",
            {
                f"{prefix}_name": self.name,
                f"{prefix}_str": self.r_str,
                f"{prefix}_rpoint": self.rpoint,
                f"{prefix}_point": self.point,
                f"{prefix}_rank": self.rank,
            },
        )


class GameResult:
    """
    1ゲームの対局結果および集計ルールを管理するクラス

    各プレイヤー（東家〜北家）の成績、対局のタイムスタンプ、供託などのゲーム結果情報に加え、
    三人打ち/四人打ちのモード設定や順位点などの計算規則を保持する。

    """

    def __init__(self, **kwargs: Any) -> None:
        """
        GameResult クラスの初期化

        引数で受け取ったキーワード引数を元にデータを設定し、スコアの再計算を行う。
        ``set`` メソッドが対応するキー（``ts``, ``p1_name``, ``mode`` など）を指定可能。

        Args:
            **kwargs (Any): 初期データおよびルール設定用のキーワード引数。

        """
        # ゲーム結果
        self.ts: str = ""
        """タイムスタンプ"""
        self.p1: Score = Score()
        """東家成績"""
        self.p2: Score = Score()
        """南家成績"""
        self.p3: Score = Score()
        """西家成績"""
        self.p4: Score = Score()
        """北家成績"""
        self.comment: Optional[str] = None
        """ゲームコメント"""
        self.deposit: int = 0
        """供託"""

        # 付属情報
        self.mode: Literal[3, 4] = 4
        """集計モード(三人打ち/四人打ち)"""
        self.rule_version: str = ""
        """ルール識別子"""
        self.origin_point: int = 250
        """配給原点"""
        self.return_point: int = 300
        """返し点"""
        self.rank_point: list[int] = [30, 10, -10, -30]
        """順位点"""
        self.draw_split: bool = False
        """同着時に順位点を山分けにするか"""
        self.source: Optional[str] = None
        """データ入力元識別子"""

        self.calc(**kwargs)

    def __bool__(self) -> bool:
        """
        オブジェクトの真偽値を評価する。

        Returns:
            bool:
                - *True*: 全プレイヤーの名前と素点文字列が入力されている
                - *False*: いずれかが欠けている

        """
        return all(self.to_list("name") + self.to_list("str"))

    def __eq__(self, other: Any) -> bool:
        """
        他の GameResult オブジェクトと等価性を比較する。

        モード、タイムスタンプ、各プレイヤーの名前と素点（rpoint）、ルール、コメント、ソースの値を比較して真偽を返す。

        Args:
            other (Any): 比較対象のオブジェクト。

        Returns:
            bool:
                - *True*: すべての値が一致
                - *False*: 不一致の値がある

        """
        if not isinstance(other, GameResult):
            return NotImplemented

        return all(
            [
                self.mode == other.mode,
                self.ts == other.ts,
                self.p1.name == other.p1.name,
                self.p1.rpoint == other.p1.rpoint,
                self.p2.name == other.p2.name,
                self.p2.rpoint == other.p2.rpoint,
                self.p3.name == other.p3.name,
                self.p3.rpoint == other.p3.rpoint,
                self.p4.name == other.p4.name,
                self.p4.rpoint == other.p4.rpoint,
                self.rule_version == other.rule_version,
                self.comment == other.comment,
                self.source == other.source,
            ]
        )

    def __lt__(self, other: Any) -> bool:
        """
        タイムスタンプを基準にオブジェクトの大小（前後）関係を比較する。

        Args:
            other (Any): 比較対象のオブジェクト。

        Returns:
            bool: 自身のタイムスタンプが相手より古い（小さい）場合は True、それ以外は False。

        """
        if not isinstance(other, GameResult):
            return NotImplemented
        return self.ts < other.ts

    def has_valid_data(self) -> bool:
        """
        DB更新に必要な必須データがすべて揃っているかチェックする。

        Returns:
            bool: タイムスタンプが存在し、全プレイヤーのスコアデータおよび順位が有効であれば True、それ以外は False。

        """
        # スコアデータ
        match self.mode:
            case 3:
                score_data = all(
                    [
                        self.p1.has_valid_data(),
                        self.p2.has_valid_data(),
                        self.p3.has_valid_data(),
                    ]
                )
            case 4:
                score_data = all(
                    [
                        self.p1.has_valid_data(),
                        self.p2.has_valid_data(),
                        self.p3.has_valid_data(),
                        self.p4.has_valid_data(),
                    ]
                )
            case _:
                score_data = False

        return all([self.ts, isinstance(self.ts, str), score_data, all(self.to_list("rank"))])

    def set(self, **kwargs: Any) -> None:
        """
        外部から受け取ったキーワード引数を解析し、対応するプロパティにデータを取り込む。

        文字列の正規化や、型チェックを行った上で各属性へ割り当てる。

        Args:
            **kwargs (Any): 設定するデータのキーワード引数。
                接頭辞付きプレイヤーデータ（例: `p1_name`, `p2_str`）や
                ゲーム設定（例: `mode`, `ts`, `rank_point`）を受け付ける。

        """

        def _normalize_score_string(s: str) -> str:
            """
            素点文字列の正規化

            Args:
                s (str): 入力文字列

            Returns:
                str: 正規化後の文字列

            """
            s = s.strip()
            s = re.sub(r"(-)+|(\+)+", r"\1\2", s)  # 連続した符号を集約
            s = re.sub(r"(-|\+)0+", r"\1", s)  # 符号の直後のゼロを削除
            if s != "0":  # 先頭のゼロとプラス記号を削除
                s = re.sub(r"^[0+]+", "", s)
            return s

        def _set_score_attr(score: Score, prefix: str, key: str, value: object) -> None:
            """
            Scoreオブジェクトに属性を設定

            Args:
                score (Score): 対象スコアオブジェクト
                prefix (str): プレイヤーポジション (p1-p4)
                key (str): 属性名
                value (object): 設定値

            """
            match key:
                case "name":
                    score.name = str(value)
                case "str":
                    score.r_str = _normalize_score_string(str(value))
                case "r_str":
                    score.r_str = str(value)
                case "rpoint" if isinstance(value, int):
                    score.rpoint = value
                case "point" if isinstance(value, (float, int)):
                    score.point = float(value)
                case "rank" if isinstance(value, (float, int)):
                    score.rank = value

        # プレイヤースコア設定
        for prefix in ("p1", "p2", "p3", "p4"):
            score_obj = cast(Score, getattr(self, prefix))
            for attr in ("name", "str", "r_str", "rpoint", "point", "rank"):
                key = f"{prefix}_{attr}"
                if key in kwargs:
                    _set_score_attr(score_obj, prefix, attr, kwargs[key])

        # ゲーム設定
        if "mode" in kwargs and isinstance(kwargs["mode"], int):
            if kwargs["mode"] in (3, 4):
                self.mode = kwargs["mode"]  # type: ignore[assignment]
        if "ts" in kwargs and isinstance(kwargs["ts"], str):
            self.ts = kwargs["ts"]
        if "rule_version" in kwargs and isinstance(kwargs["rule_version"], str):
            self.rule_version = str(kwargs["rule_version"])
        if "deposit" in kwargs and isinstance(kwargs["deposit"], int):
            self.deposit = int(kwargs["deposit"])
        if "origin_point" in kwargs and isinstance(kwargs["origin_point"], int):
            self.origin_point = int(kwargs["origin_point"])
        if "return_point" in kwargs and isinstance(kwargs["return_point"], int):
            self.return_point = int(kwargs["return_point"])
        if "rank_point" in kwargs and isinstance(kwargs["rank_point"], list):
            self.rank_point = kwargs["rank_point"]
        if "draw_split" in kwargs and isinstance(kwargs["draw_split"], bool):
            self.draw_split = kwargs["draw_split"]
        if "comment" in kwargs:
            self.comment = kwargs["comment"]
        if "source" in kwargs:
            self.source = kwargs["source"]

    def to_dict(self) -> "ScoreDict":
        """
        オブジェクト全体のデータをフラットな辞書形式に変換する。

        Returns:
            ScoreDict: DB保存やAPI返却に適した、プレフィックス付きキーを含む対局結果データ。

        """
        return {
            "ts": self.ts,
            **self.p1.to_dict("p1"),
            **self.p2.to_dict("p2"),
            **self.p3.to_dict("p3"),
            **self.p4.to_dict("p4"),
            "deposit": self.deposit,
            "comment": self.comment,
            "rule_version": self.rule_version,
            "source": self.source,
            "mode": self.mode,
        }

    def to_text(self, kind: Literal["simple", "detail", "logging"] = "simple") -> str:
        """
        対局結果のデータを可読性の高いテキスト（文字列）形式に変換する。

        Args:
            kind (Literal, optional): 出力するテキストの表示形式。

                - *simple*: 簡易情報 (Default)
                - *detail*: 詳細な対局データ
                - *logging*: ログ出力用のフォーマット

        Returns:
            str: 指定された形式で整形された対局結果テキスト。

        """
        ret_text: str = ""
        match kind:
            case "simple":
                ret_text += f"[{self.p1.name} {self.p1.r_str}] "
                ret_text += f"[{self.p2.name} {self.p2.r_str}] "
                ret_text += f"[{self.p3.name} {self.p3.r_str}] "
                ret_text += f"[{self.p4.name} {self.p4.r_str}] " if self.mode == 4 else ""
                ret_text += f"[供託 {self.deposit}] [{self.comment if self.comment else None}]"
            case "detail":
                ret_text += f"[{self.p1.rank}位 {self.p1.name} {self.p1.rpoint * 100}点 ({self.p1.point}pt)] ".replace("-", "▲")
                ret_text += f"[{self.p2.rank}位 {self.p2.name} {self.p2.rpoint * 100}点 ({self.p2.point}pt)] ".replace("-", "▲")
                ret_text += f"[{self.p3.rank}位 {self.p3.name} {self.p3.rpoint * 100}点 ({self.p3.point}pt)] ".replace("-", "▲")
                ret_text += f"[{self.p4.rank}位 {self.p4.name} {self.p4.rpoint * 100}点 ({self.p4.point}pt)] ".replace("-", "▲") if self.mode == 4 else ""
                ret_text += f"[供託 {self.deposit * 100}点] "
                ret_text += f"[{self.comment if self.comment else None}]"
            case "logging":
                ret_text += f"ts={self.ts}, deposit={self.deposit}, rule_version={self.rule_version}, "
                ret_text += f"p1={self.p1.to_dict('p1')}, p2={self.p2.to_dict('p2')}, p3={self.p3.to_dict('p3')}, "
                ret_text += f"p4={self.p4.to_dict('p4')}, " if self.mode == 4 else ""
                ret_text += f"comment={self.comment if self.comment else None}, source={self.source}"

        return ret_text

    def to_list(self, kind: Literal["name", "str", "rpoint", "point", "rank"] = "name") -> list[str | int | float]:
        """
        各プレイヤーの指定された属性の値をリストにして取得する。

        Args:
            kind (Literal, optional): 取得したい Score クラスの属性名

                - *name*: プレイヤー名 (Default)
                - *str*: 入力された素点情報
                - *rpoint*: 素点
                - *point*: ポイント
                - *rank*: 順位

        Returns:
            list[str | int | float]: 各プレイヤーから抽出した属性値のリスト。

        """
        ret_list: list[str | int | float] = []
        match kind:
            case "name":
                ret_list = [self.p1.name, self.p2.name, self.p3.name, self.p4.name]
            case "str":
                ret_list = [self.p1.r_str, self.p2.r_str, self.p3.r_str, self.p4.r_str]
            case "rpoint":
                ret_list = [self.p1.rpoint, self.p2.rpoint, self.p3.rpoint, self.p4.rpoint]
            case "point":
                ret_list = [self.p1.point, self.p2.point, self.p3.point, self.p4.point]
            case "point":
                ret_list = [self.p1.point, self.p2.point, self.p3.point, self.p4.point]
            case "rank":
                ret_list = [self.p1.rank, self.p2.rank, self.p3.rank, self.p4.rank]

        return ret_list[: self.mode]

    def calc(self, **kwargs: Any) -> None:
        """
        入力されたデータを元に、スコア・順位・ポイントの計算を行う。

        Args:
            **kwargs (Any): 更新するデータがある場合に指定するキーワード引数。

        """
        if kwargs:
            self.set(**kwargs)

        match self.mode:
            case 3:
                if all([self.p1.has_valid_data(), self.p2.has_valid_data(), self.p3.has_valid_data()]):
                    self.set(**self._calculation_point3())
                    self.p4 = Score()
            case 4:
                if all([self.p1.has_valid_data(), self.p2.has_valid_data(), self.p3.has_valid_data(), self.p4.has_valid_data()]):
                    self.set(**self._calculation_point4())
            case _:
                raise RuntimeError

    def _normalized_expression(self, expr: str) -> int:
        """
        入力文字列を式として評価し、計算結果を返す

        Args:
            expr (str): 入力式

        Returns:
            int: 計算結果

        """
        normalized: list[str] = []

        for token in re.findall(r"\d+|[+\-*/]", expr):
            if isinstance(token, str):
                if token.isnumeric():
                    normalized.append(str(int(token)))
                else:
                    normalized.append(token)

        return int(eval("".join(normalized)))

    def _calculation_point3(self) -> dict[str, Any]:
        """
        獲得ポイントと順位を計算する(三人打ち)

        Returns:
            dict[str, Any]: 更新用辞書(順位と獲得ポイントのデータ)

        """
        # 計算用データフレーム
        score_df = pd.DataFrame({"rpoint": [self._normalized_expression(str(x)) for x in self.to_list("str")]}, index=["p1", "p2", "p3"])

        work_rank_point = self.rank_point.copy()  # ウマ
        work_rank_point[0] += int((self.return_point - self.origin_point) / 10 * 3)  # オカ

        # 席順
        score_df["rank"] = score_df["rpoint"].rank(ascending=False, method="first").astype("int")

        # 獲得ポイントの計算 (素点-配給原点)/10+順位点
        score_df["position"] = score_df["rpoint"].rank(ascending=False, method="first").astype("int")  # 加算する順位点リストの位置
        score_df["point"] = (score_df["rpoint"] - self.return_point) / 10 + score_df["position"].apply(lambda p: work_rank_point[p - 1])
        score_df["point"] = score_df["point"].apply(lambda p: float(f"{p:.1f}"))  # 桁ブレ修正

        # 返却値用辞書
        ret_dict = {f"{k}_{x}": v for x in score_df.columns for k, v in score_df[x].to_dict().items()}
        ret_dict.update(deposit=int(self.origin_point * 3 - score_df["rpoint"].sum()))

        return ret_dict

    def _calculation_point4(self) -> dict[str, Any]:
        """
        獲得ポイントと順位を計算する(四人打ち)

        Returns:
            dict[str, Any]: 更新用辞書(順位と獲得ポイントのデータ)

        """

        def point_split(point: list[int]) -> list[int]:
            """
            順位点を山分けする

            Args:
                point (list[int]): 山分けするポイントのリスト

            Returns:
                list[int]: 山分けした結果

            """
            new_point = [int(sum(point) / len(point))] * len(point)
            if sum(point) % len(point):
                new_point[0] += sum(point) % len(point)
                if sum(point) < 0:
                    new_point = list(map(lambda x: x - 1, new_point))

            return new_point

        # 計算用データフレーム
        score_df = pd.DataFrame({"rpoint": [self._normalized_expression(str(x)) for x in self.to_list("str")]}, index=["p1", "p2", "p3", "p4"])

        work_rank_point = self.rank_point.copy()  # ウマ
        work_rank_point[0] += int((self.return_point - self.origin_point) / 10 * 4)  # オカ

        if self.draw_split:  # 山分け
            score_df["rank"] = score_df["rpoint"].rank(ascending=False, method="min").astype("int")

            # 順位点リストの更新
            match "".join(score_df["rank"].sort_values().to_string(index=False).split()):
                case "1111":  # 2.5/2.5/2.5/2.5
                    work_rank_point = point_split(work_rank_point)
                    score_df["rank"] = score_df["rank"].replace(1, 2.5)
                case "1114":  # 2/2/2/4
                    new_point = point_split(work_rank_point[0:3])
                    work_rank_point[0] = new_point[0]
                    work_rank_point[1] = new_point[1]
                    work_rank_point[2] = new_point[2]
                    score_df["rank"] = score_df["rank"].replace(1, 2)
                case "1134":  # 1.5/1.5/3/4
                    new_point = point_split(work_rank_point[0:2])
                    work_rank_point[0] = new_point[0]
                    work_rank_point[1] = new_point[1]
                    score_df["rank"] = score_df["rank"].replace(1, 1.5)
                case "1133":  # 1.5/1.5/3.5/3.5
                    new_point = point_split(work_rank_point[0:2])
                    work_rank_point[0] = new_point[0]
                    work_rank_point[1] = new_point[1]
                    score_df["rank"] = score_df["rank"].replace(1, 1.5)
                    new_point = point_split(work_rank_point[2:4])
                    work_rank_point[2] = new_point[0]
                    work_rank_point[3] = new_point[1]
                    score_df["rank"] = score_df["rank"].replace(3, 3.5)
                case "1222":  # 1/3/3/3
                    new_point = point_split(work_rank_point[1:4])
                    work_rank_point[1] = new_point[0]
                    work_rank_point[2] = new_point[1]
                    work_rank_point[3] = new_point[2]
                    score_df["rank"] = score_df["rank"].replace(2, 3)
                case "1224":  # 1/2.5/2.5/4
                    new_point = point_split(work_rank_point[1:3])
                    work_rank_point[1] = new_point[0]
                    work_rank_point[2] = new_point[1]
                    score_df["rank"] = score_df["rank"].replace(2, 2.5)
                case "1233":  # 1/2/3.5/3.5
                    new_point = point_split(work_rank_point[2:4])
                    work_rank_point[2] = new_point[0]
                    work_rank_point[3] = new_point[1]
                    score_df["rank"] = score_df["rank"].replace(3, 3.5)
                case _:
                    pass

        else:  # 席順
            score_df["rank"] = score_df["rpoint"].rank(ascending=False, method="first").astype("int")

        # 獲得ポイントの計算 (素点-配給原点)/10+順位点
        score_df["position"] = score_df["rpoint"].rank(ascending=False, method="first").astype("int")  # 加算する順位点リストの位置
        score_df["point"] = (score_df["rpoint"] - self.return_point) / 10 + score_df["position"].apply(lambda p: work_rank_point[p - 1])
        score_df["point"] = score_df["point"].apply(lambda p: float(f"{p:.1f}"))  # 桁ブレ修正

        # 返却値用辞書
        ret_dict = {f"{k}_{x}": v for x in score_df.columns for k, v in score_df[x].to_dict().items()}
        ret_dict.update(deposit=int(self.origin_point * 4 - score_df["rpoint"].sum()))

        return ret_dict

    @property
    def rpoint_sum(self) -> int:
        """
        素点合計

        Returns:
            int: 素点合計

        """
        if not all(self.to_list("rank")):  # 順位が確定していない場合は先に計算
            self.calc()

        return sum(cast(list[int], self.to_list("rpoint")))
