"""
libs/commands/help/entry.py
"""

import textwrap
from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain.section import SubCommands
from libs.functions import lookup
from libs.types import CommandType, StyleOptions
from libs.utils import dictutil, formatter
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class HelpConfig(SubCommands):
    """helpセクション処理"""

    def __init__(self) -> None:
        self.default_commandword: str = "麻雀ヘルプ"
        self.section: str = str(CommandType.HELP)
        self.default_reset()


def main(m: "MessageParserProtocol") -> None:
    """
    ヘルプ処理エントリーポイント

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    m.status.command_type = CommandType.HELP
    g.params = dictutil.placeholder(g.cfg.help, m)

    help_message(m)
    m.post.ts = m.data.event_ts
    m.post.thread_title = "ヘルプメッセージ"


def help_message(m: "MessageParserProtocol") -> None:
    """
    呼び出しキーワードヘルプメッセージ

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    g.params.update_from_dict(
        {
            "source": g.cfg.resolve_channel_id(m.status.source),
            "separate": lookup.resolve_separate_flag(m),
        }
    )
    g.cfg.rule.status_update(g.params.placeholder())
    g.params.update_setting(g.cfg.config_file, "default_rule", str)

    m.set_message(
        textwrap.dedent(f"""\
        使い方：<呼び出しワード> [検索範囲] [対象メンバー] [オプション]
        集計対象ルール識別子：{g.params.rule_version}
        """),
        StyleOptions(title="機能呼び出し"),
    )
    m.set_message(
        textwrap.dedent(f"""\
        呼び出しワード：{"、".join(lookup.resolve_commands(g.params.rule_version, CommandType.RESULTS))}
        検索範囲デフォルト：{g.cfg.results.aggregation_range}
        """),
        StyleOptions(title="成績サマリ", indent=1, sub_title=True),
    )
    m.set_message(
        textwrap.dedent(f"""\
        呼び出しワード：{"、".join(lookup.resolve_commands(g.params.rule_version, CommandType.GRAPH))}
        検索範囲デフォルト：{g.cfg.graph.aggregation_range}
        """),
        StyleOptions(title="成績グラフ", indent=1, sub_title=True),
    )
    m.set_message(
        textwrap.dedent(f"""\
        呼び出しワード：{"、".join(lookup.resolve_commands(g.params.rule_version, CommandType.RANKING))}
        検索範囲デフォルト：{g.cfg.ranking.aggregation_range}
        規定打数デフォルト：全体ゲーム数 × {g.cfg.ranking.stipulated_rate} ＋ 1
        出力制限デフォルト：上位 {g.cfg.ranking.ranked} 名
        """),
        StyleOptions(title="ランキング", indent=1, sub_title=True),
    )
    m.set_message(
        textwrap.dedent(f"""\
        呼び出しワード：{"、".join(lookup.resolve_commands(g.params.rule_version, CommandType.REPORT))}
        検索範囲デフォルト：{g.cfg.report.aggregation_range}
        """),
        StyleOptions(title="レポート", indent=1, sub_title=True),
    )
    m.set_message(
        f"呼び出しワード：{'、'.join(lookup.resolve_commands(g.params.rule_version, CommandType.MEMBER_LIST))}",
        StyleOptions(title="メンバー一覧", indent=1, sub_title=True),
    )
    m.set_message(
        f"呼び出しワード：{'、'.join(lookup.resolve_commands(g.params.rule_version, CommandType.TEAM_LIST))}",
        StyleOptions(title="チーム一覧", indent=1, sub_title=True),
    )
    m.set_message(  # 検索範囲
        ExtDt.print_range(),
        StyleOptions(title="検索範囲に指定できるワード"),
    )

    # メモ機能
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
        メモ記録ワード：{"、".join(g.cfg.rule.data[g.params.rule_version].remarks)}

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
        デフォルトルール識別子：{g.params.default_rule}
        チャンネル個別設定：{channel_config.name if channel_config else "---"}
        セパレート機能：{"有効" if g.params.separate else "無効"}
        """),
        StyleOptions(title="チャンネル設定情報"),
    )

    # 非表示項目を削除
    m.delete_items(formatter.dropitems_list())
