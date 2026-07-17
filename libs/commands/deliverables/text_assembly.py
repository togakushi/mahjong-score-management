"""
メッセージテキストの組み立て
"""

import textwrap
from typing import TYPE_CHECKING

from table2ascii import Alignment, PresetStyle, table2ascii

import libs.global_value as g
from libs.functions import adjusting, lookup
from libs.types import StyleOptions
from libs.utils import dictutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def get_members_list(m: "MessageParserProtocol") -> str:
    """
    登録済みのメンバー一覧を取得する

    Args:
        m (MessageParserProtocol): メッセージを蓄積・設定するためのメッセージデータオブジェクト。

    Returns:
        str: メンバーリスト

    """
    g.params = dictutil.placeholder(g.cfg.summary, m)
    g.params.rule_version = g.cfg.setting.default_rule
    member_df = g.params.read_data("MEMBER_INFO")

    if member_df.empty:
        output = "メンバーは登録されていません。"
    else:
        member_df = adjusting.add_units(member_df.rename(columns={"last_update": "playtime"}).fillna("記録なし"))
        if g.params.verbose:
            alignments_data = [Alignment.LEFT, Alignment.LEFT, Alignment.RIGHT, Alignment.RIGHT]
            header_data = ["メンバー名", "最終更新日", "経過日数", "総対戦数"]
            body_data = member_df.filter(
                items=[
                    "name",
                    "playtime",
                    "elapsed_day",
                    "game_count",
                ]
            ).to_dict(orient="split")["data"]
        else:
            alignments_data = [Alignment.LEFT, Alignment.LEFT]
            header_data = ["表示名", "登録されている名前"]
            body_data = member_df.filter(items=["name", "alias"]).to_dict(orient="split")["data"]

        output = table2ascii(
            header=header_data,
            body=body_data,
            alignments=alignments_data,
            cell_padding=0,
            style=PresetStyle.ascii_borderless,
        )

    return output


def get_team_list() -> str:
    """
    チームの登録状況を取得する

    Returns:
        str: チームリスト

    """
    team_list: list[list[str]] = []
    for team_name in g.cfg.team.lists:
        if member := ", ".join(g.cfg.team.member(team_name)):
            team_list.append([team_name, member])
        else:
            team_list.append([team_name, "未エントリー"])

    if team_list:
        output = table2ascii(
            header=["チーム名", "所属メンバー"],
            body=team_list,
            alignments=[Alignment.LEFT, Alignment.LEFT],
            style=PresetStyle.ascii_borderless,
        )
    else:
        output = "チームは登録されていません。"

    return output


def help_message(m: "MessageParserProtocol") -> None:
    """
    ユーザーに提示する各機能の呼び出しキーワードや設定情報のヘルプメッセージを動的に構築する。

    内部では、チャンネルの個別設定やルール識別子の状態を最新に更新した上で、以下の各セクションに関する
    ヘルプ内容（呼び出しワードや規定打数などのデフォルト値）を、 ``m.set_message`` を用いて多層的に組み立てる。

    Args:
        m (MessageParserProtocol): メッセージを蓄積・設定するためのメッセージデータオブジェクト。

    構築されるヘルプ情報セクション:
        - **コマンド呼び出し**: 基本的な使い方のフォーマットと適用中のルール識別子。
        - **集計コマンド (SUMMARY)**: 集計コマンドの呼び出しワードと検索範囲の初期値。
        - **分析コマンド (ANALYSIS)**: 分析コマンドの呼び出しワード、検索範囲、規定打数の計算規則、出力制限人数。
        - **メンバー・チーム一覧**: 登録されているメンバーやチームのリストを出力する呼び出しワード。
        - **検索範囲**: 期間指定などで利用できる有効な検索ワードの一覧。
        - **メモ機能**: 個別カウントや役満カウントなどのレギュレーションに準じたメモ記録ワードと仕様。
        - **ルールセット・レギュレーション**: 卓外清算ワード（個人/チーム）やルール情報の詳細。
        - **チャンネル設定情報**: 現在のチャンネルID、デフォルトルール、個別設定ファイルの有無、セパレート機能の成否。

    """
    # パラメータ更新
    m.status.command_type = m.COMMAND_TYPE.HELP
    rule_version = lookup.get_current_rule_version(m, g.cfg.help.command_suffix)

    g.params.update_from_dict(
        {
            **g.cfg.rule.to_dict(rule_version),
            "source": g.cfg.resolve_channel_id(m.status.source),
            "separate": lookup.resolve_separate_flag(m),
        }
    )
    g.cfg.rule.status_update(g.params.placeholder())
    g.params.update_setting(g.cfg.config_file, "default_rule", str)

    # コマンド
    m.set_message(
        textwrap.dedent("""\
        使い方：<呼び出しワード> [検索範囲] [ターゲット] [オプション]
        """),
        StyleOptions(title="コマンド呼び出し"),
    )
    m.set_message(
        g.cfg.summary.help_string(g.cfg.summary.section),
        StyleOptions(title=g.cfg.summary.command_name, indent=1, sub_title=True),
    )
    m.set_message(
        g.cfg.analysis.help_string(g.cfg.analysis.section),
        StyleOptions(title=g.cfg.analysis.command_name, indent=1, sub_title=True),
    )
    m.set_message(
        g.cfg.member.help_string(g.cfg.member.section),
        StyleOptions(title=g.cfg.member.command_name, indent=1, sub_title=True),
    )
    m.set_message(
        g.cfg.team.help_string(g.cfg.team.section),
        StyleOptions(title=g.cfg.team.command_name, indent=1, sub_title=True),
    )

    # ショートカット
    if g.cfg.shortcut:
        m.set_message(
            "\n".join([f"{k}\t→ {v}" for k, v in g.cfg.shortcut.items()]),
            StyleOptions(title="コマンドショートカット"),
        )

    # 検索範囲
    m.set_message(
        ExtDt.print_range(),
        StyleOptions(title="検索範囲に指定できるワード", keep_indent=True),
    )

    # メモ機能
    if g.cfg.rule.remarks_words:
        # メモ記録ワード探索
        if not (remarks_words := g.cfg.rule.data[g.params.rule_version].remarks):
            if g.cfg.setting.remarks_suffix:
                remarks_words = [
                    f"{keywords}{suffix}" for keywords in g.cfg.rule.data[g.params.rule_version].keywords for suffix in g.cfg.setting.remarks_suffix
                ]
            else:
                remarks_words = g.cfg.rule.remarks_words

        remarks_type1: str = ""
        if words := lookup.regulation_list(1, g.params.rule_version):
            remarks_type1 += "個別カウントワード：" + "、".join(words)
        else:
            if g.cfg.rule.get_undefined_word(g.params.default_rule) == 1:
                remarks_type1 += "個別カウントワード：未登録ワードのすべてを個別にカウント"

        remarks_type0: str = ""
        if words := lookup.regulation_list(0, g.params.rule_version):
            remarks_type0 += "役満カウントワード：" + "、".join(words)
        else:
            if g.cfg.rule.get_undefined_word(g.params.default_rule) == 0:
                remarks_type0 += "役満カウントワード：未登録ワードのすべてを役満としてカウント"

        m.set_message(
            textwrap.dedent(f"""\
            使い方：<メモ記録ワード> <対象メンバー> <内容>
            メモ記録ワード：{"、".join(remarks_words)}

            {remarks_type1}
            {remarks_type0}
            """),
            StyleOptions(title="メモ機能", keep_blank=True),
        )

    # ルールセット
    m.set_message(
        g.cfg.rule.print(g.params.rule_version),
        StyleOptions(title="ルールセット情報"),
    )

    # レギュレーション
    if g.cfg.rule.remarks_words:
        regulation: str = ""
        if words := lookup.regulation_list(2, g.params.rule_version):
            regulation += "卓外清算ワード(個人)：\n"
            for word in words:
                regulation += f"\t{word}\n"
            regulation += "\n"

        if words := lookup.regulation_list(3, g.params.rule_version):
            regulation += "卓外清算ワード(チーム)：\n"
            for word in words:
                regulation += f"\t{word}\n"
            regulation += "\n"
        if regulation:
            m.set_message(regulation, StyleOptions(title="レギュレーション", keep_blank=True, keep_indent=True))

    # その他
    channel_config = g.params.channel_config
    m.set_message(
        textwrap.dedent(f"""\
        チャンネル識別子：{g.params.source}
        デフォルトルール識別子：{g.params.rule_version}
        チャンネル個別設定：{channel_config.name if channel_config else "---"}
        セパレート機能：{"有効" if g.params.separate else "無効"}
        """),
        StyleOptions(title="チャンネル設定情報"),
    )

    # 非表示項目を削除
    m.delete_items(dictutil.dropitems_list())
