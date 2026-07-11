"""
libs/domain/placeholder.py
"""

import logging
import re
import textwrap
from dataclasses import dataclass, field, fields
from math import ceil
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import pandas as pd

from libs.domain.datamodels import ParameterData
from libs.functions import lookup
from libs.types import ServiceType
from libs.utils import dbutil, textutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class PlaceholderBuilder(ParameterData):
    """プレースホルダ構築クラス"""

    service_type: ServiceType = field(default=ServiceType.UNKNOWN)
    """連携先サービス"""
    command: str = field(default="")
    """コマンド名"""
    channel_config: Optional["Path"] = field(default=None)
    """チャンネル個別設定状況

    - *Path*: 追加設定ファイルパス
    - *None*: 個別設定を利用していない
    """

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
    """引数で受け付けたプレイヤーのリスト"""
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
    aggregate_unit: Literal["A", "M", "Y", None] = field(default=None)
    """レポート生成用日付範囲デフォルト値

    - *A*: 全期間
    - *M*: 月別
    - *Y*: 年別
    - *None*: 未定義
    """
    target_count: int = field(default=0)
    """直近対戦数指定"""

    starttime: Union[str, ExtDt, None] = field(default=None)
    """集計開始日時"""
    endtime: Union[str, ExtDt, None] = field(default=None)
    """集計終了日時"""
    onday: Union[str, ExtDt, None] = field(default=None)
    """time_adjust修正を含まない日時"""

    # 動作/表示変更フラグ
    comparisons: bool = field(default=False)
    """比較表示"""
    verbose: bool = field(default=False)
    """詳細情報表示切替"""
    game_results: bool = field(default=False)
    """ゲーム結果表示"""
    versus: bool = field(default=False)
    """対戦フラグ"""
    order: bool = field(default=False)
    """順位フラグ"""
    rating: bool = field(default=False)
    """レーティング表示フラグ"""
    raw_score: bool = field(default=False)
    """素点分析表示"""
    anonymous: bool = field(default=False)
    """匿名化フラグ"""
    mapping_dict: dict[str, str] = field(default_factory=dict)
    """匿名化用マッピング辞書"""
    fourfold: bool = field(default=True)
    """縦持ち/横持ちデータ判定"""

    # 出力関連
    guest_mark: str = field(default="※")
    """ゲスト無効時に未登録メンバーに付与する印"""
    format: Literal["default", "csv", "txt"] = field(default="default")
    """出力フォーマット指定"""
    graph: bool = field(default=False)
    """グラフ出力"""
    report: bool = field(default=False)
    """レポート出力"""
    filename: str = field(default="")
    """出力ファイル名"""

    # その他
    database_file: Union[str, "Path"] = field(default="")
    """成績管理データベースファイル名"""
    logging_verbose: int = field(default=0)
    """デバッグ情報出力レベル"""

    def update_from_dict(self, input_dict: dict[str, Any]) -> None:
        """
        辞書の内容で値を更新する

        Args:
            input_dict (dict[str,Any]): 更新内容

        """
        field_list: list[str] = [x.name for x in fields(self)]
        for k, v in input_dict.items():
            if k in field_list:
                setattr(self, k, v)

    def update_setting(self, main_config: "Path", key_name: str, val_type: type, fallback: Any = None) -> None:
        """
        優先度順に key_name を探索して値を更新する

        Args:
            main_config (Path): メイン設定ファイルパス
            key_name (str): 探索するキー名
            val_type (type): 取り込む値の型 (bool, str)
            fallback (Any): 見つからなかった場合にセットする値

                - *None* が指定されているときは値を更新しない

        Note:
            探索優先順序

            1. 個別設定ファイル内settingセクション
            2. メイン設定ファイル内チャンネル個別セクション
            3. メイン設定ファイル内サービス別セクション
            4. メイン設定ファイル内settingセクション

        """
        value: Optional[Any] = None
        # 個別設定ファイル内探索
        if self.channel_config:
            value = lookup.get_config_value(
                config_file=self.channel_config,
                section="setting",
                name=key_name,
                val_type=val_type,
                fallback=None,
            )
            if value is not None:
                setattr(self, key_name, value)
                return

        # メイン設定ファイル内探索
        for section_name in [self.source, self.service_type, "setting"]:
            value = lookup.get_config_value(
                config_file=main_config,
                section=section_name,
                name=key_name,
                val_type=val_type,
                fallback=None,
            )
            if value is not None:
                setattr(self, key_name, value)
                return

        if fallback is not None:
            setattr(self, key_name, fallback)

    def query_modification(self, query: str) -> str:
        """
        クエリをオプションの内容で修正する

        Args:
            query (str): 修正するクエリ

        Returns:
            str: 修正後のクエリ

        """
        if self.individual:  # 個人集計
            query = query.replace("--[individual] ", "")
            # ゲスト関連フラグ
            if self.unregistered_replace:
                query = query.replace("--[unregistered_replace] ", "")
                if self.guest_skip:
                    query = query.replace("--[guest_not_skip] ", "")
                else:
                    query = query.replace("--[guest_skip] ", "")
            else:
                query = query.replace("--[unregistered_not_replace] ", "")
        else:  # チーム集計
            self.unregistered_replace = False
            self.guest_skip = True
            query = query.replace("--[team] ", "")
            if not self.friendly_fire:
                query = query.replace("--[friendly_fire] ", "")

        # 集約集計
        match self.collection:
            case "daily":
                query = query.replace("--[collection_daily] ", "")
                query = query.replace("--[collection] ", "")
                query = query.replace("--[monthly] ", "")  # 月次集約のみ
            case "weekly":
                query = query.replace("--[collection_weekly] ", "")
                query = query.replace("--[collection] ", "")
                query = query.replace("--[monthly] ", "")  # 月次集約のみ
            case "monthly":
                query = query.replace("--[collection_monthly] ", "")
                query = query.replace("--[collection] ", "")
                query = query.replace("--[monthly] ", "")
            case "yearly":
                query = query.replace("--[collection_yearly] ", "")
                query = query.replace("--[collection] ", "")
                query = query.replace("--[yearly] ", "")
            case "all":
                query = query.replace("--[collection_all] ", "")
                query = query.replace("--[collection] ", "")
                query = query.replace("--[monthly] ", "")  # 月次集約のみ
            case _:
                query = query.replace("--[not_collection] ", "")
                query = query.replace("--[monthly] ", "")  # 月次集約のみ

        # 集計対象ルール
        if self.rule_list:
            query = query.replace("<<rule_list>>", ",".join([f":rule_{idx}" for idx, _ in enumerate(self.rule_list)]))
        else:
            query = query.replace("and rule_version in (<<rule_list>>)", "")
            query = query.replace("and results.rule_version in (<<rule_list>>)", "")
            query = query.replace("and game_info.rule_version in (<<rule_list>>)", "")

        # 集計モード
        match self.mode:
            case 3:
                query = query.replace("--[mode3] ", "")
            case 4:
                query = query.replace("--[mode4] ", "")

        # スコア入力元識別子別集計
        if self.separate:
            query = query.replace("--[separate] ", "")

        # コメント検索
        if self.search_word or self.group_length:
            query = query.replace("--[group_by] ", "")
        else:
            query = query.replace("--[not_group_by] ", "")

        if self.search_word:
            query = query.replace("--[search_word] ", "")
        else:
            query = query.replace("--[not_search_word] ", "")

        if self.group_length:
            query = query.replace("--[group_length] ", "")
        else:
            query = query.replace("--[not_group_length] ", "")
            if self.search_word:
                query = query.replace("--[comment] ", "")
            else:
                query = query.replace("--[not_comment] ", "")

        # 直近N検索用（全範囲取得してから絞る）
        if self.target_count:
            query = query.replace("and my.playtime between", "-- and my.playtime between")

        # プレイヤーリスト
        if self.player_name and self.player_list:
            query = query.replace("--[player_name] ", "")
            query = query.replace(
                "<<player_list>>",
                ", ".join([f":player_{idx}" for idx, _ in enumerate(self.player_list)]),
            )
        query = query.replace("<<guest_mark>>", self.guest_mark)

        # フラグの処理
        match self.aggregate_unit:
            case "M":
                query = query.replace("<<collection>>", "substr(collection_daily, 1, 7) as 集計")
                query = query.replace("<<group by>>", "group by 集計")
            case "Y":
                query = query.replace("<<collection>>", "substr(collection_daily, 1, 4) as 集計")
                query = query.replace("<<group by>>", "group by 集計")
            case "A":
                query = query.replace("<<collection>>", "'合計' as 集計")
                query = query.replace("<<group by>>", "")
            case _:
                query = query.replace("<<collection>>,", "-- <<collection>>")
                query = query.replace("<<group by>>", "-- <<group by>>")

        if self.interval:
            query = query.replace("<<Calculation Formula>>", "(row_number() over (order by total_count desc) - 1) / :interval")
        else:
            query = query.replace("<<Calculation Formula>>", ":interval")

        if self.undefined_word is not None:
            match self.undefined_word:
                case 0:
                    query = query.replace("<<where_string>>", "and (words.type is null or words.type = 0)")
                case 1:
                    query = query.replace("<<where_string>>", "and (words.type is null or words.type = 1)")
                case 2:
                    query = query.replace("<<where_string>>", "and (words.type is null or words.type = 2)")
                case _:
                    query = query.replace("<<where_string>>", "and (words.type = 1 or words.type = 2)")
        else:
            query = query.replace(":undefined_word", "1")

        # queryコメント削除
        query = re.sub(r"^ *--\[.*$", "", query, flags=re.MULTILINE)
        query = re.sub(r"\n+", "\n", query, flags=re.MULTILINE)

        return query

    def named_query(self, query: str) -> str:
        """
        クエリにパラメータをバインドして返す

        Args:
            query (str): SQL

        Returns:
            str: バインド済みSQL

        """
        return textwrap.dedent(
            re.sub(
                r":(\w+)",
                lambda m: repr(self.placeholder().get(m.group(1), m.group(0))),
                query,
            ),
        ).strip()

    def placeholder(self, game_count: Optional[int] = None) -> dict[str, Any]:
        """
        プレースホルダ用辞書出力

        Args:
            game_count (int, optional): 規定打数調整用対戦数. Defaults to None.

        Returns:
            dict[str, Any]: プレースホルダ

        """
        ret_dict: dict[str, Any] = {f.name: getattr(self, f.name) for f in fields(self)}

        # 規定打数更新
        if not ret_dict.get("stipulated") or game_count is not None:
            if game_count is None:
                ret_dict.update({"stipulated": 1})
            else:
                ret_dict.update({"stipulated": int(ceil(game_count * self.stipulated_rate) + 1)})

        if self.player_list:
            ret_dict.update({f"player_{idx}": x for idx, x in enumerate(self.player_list)})

        if self.target_player:
            ret_dict.update({f"target_{idx}": x for idx, x in enumerate(self.target_player)})

        if self.competition_list:
            ret_dict.update({f"competition_{idx}": x for idx, x in enumerate(self.competition_list)})

        if self.rule_list:
            ret_dict.update({f"rule_{idx}": x for idx, x in enumerate(self.rule_list)})
        else:
            ret_dict.update({"rule_0": self.rule_version})

        # 日付型変換
        for date_attr in ["starttime", "endtime", "onday"]:
            if (val := ret_dict.get(date_attr)) and isinstance(val, ExtDt):
                ret_dict.update({date_attr: val.format(ExtDt.FMT.SQL)})

        return ret_dict

    def read_data(self, keyword: str, anonymization: bool = True) -> pd.DataFrame:
        """
        データベースからデータを取得する

        Args:
            keyword (str): SQL選択キーワード
            anonymization (bool): 匿名化フラグを評価する

        Returns:
            pd.DataFrame: 集計結果

        """
        query = self.query_modification(dbutil.query(keyword))

        if self.logging_verbose & 0x01:
            print(f">>> params={self.placeholder()}")
            print(f">>> SQL: {keyword} -> {self.database_file}\n{self.named_query(query)}")

        try:
            query_start_time = ExtDt().dt.timestamp()
            df = pd.read_sql(
                sql=query,
                con=dbutil.connection(self.database_file),
                params=self.placeholder(),
            )
            query_end_time = ExtDt().dt.timestamp()
        except pd.errors.DatabaseError as err:
            logging.error("DatabaseError: %s", err)
            logging.error("SQL: %s, DATABASE: %s", keyword, self.database_file)
            logging.error("params=%s", self.placeholder())
            logging.error("query: %s", self.named_query(query))

        # 匿名化
        if anonymization and self.anonymous:
            if "name" in df.columns:
                if not self.mapping_dict:
                    self.mapping_dict = textutil.anonymous_mapping(df["name"].unique().tolist())
                df["name"] = df["name"].replace(self.mapping_dict)

        if self.logging_verbose & 0x02:
            print("=" * 80)
            print(df.to_string())

        logging.debug("SQL: %s, time: %s", keyword, query_end_time - query_start_time)
        return df
