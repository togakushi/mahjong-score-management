"""
libs/commands/help.py
"""

import textwrap
from typing import TYPE_CHECKING

import libs.global_value as g
from libs.domain.datamodels import CommandAttrs
from libs.domain.section import BaseSection
from libs.functions import lookup
from libs.types import CommandType, StyleOptions
from libs.utils import dictutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


class HelpConfig(BaseSection, CommandAttrs):
    """
    ヘルプ表示コマンド（helpセクション）の設定を管理するクラス。

    設定ファイルからヘルプコマンド固有のパラメータを読み込み、保持する役割を持つ。

    """

    def __init__(self) -> None:
        """
        HelpConfig クラスの初期化。

        デフォルトのコマンドワードおよびセクション名を設定し、設定値を初期状態にリセットする。
        """
        self.default_commandword: str = "麻雀ヘルプ"
        self.section: str = str(CommandType.HELP)
        self.default_reset()

    def register(self) -> None:
        """ディスパッチャー登録"""
        for command in self.commandwords_list():
            g.keyword_dispatcher.update({command: main})


def main(m: "MessageParserProtocol") -> None:
    """
    ヘルプ処理のエントリーポイント。

    受信したメッセージデータに基づいてヘルプパラメータを解析し、ユーザー向けのヘルプ案内メッセージを構築する。
    メッセージの送信スレッドのタイトルやタイムスタンプなどの投稿メタデータもここで設定される。

    Args:
        m (MessageParserProtocol): 解析済みのテキストやステータスを含むメッセージデータオブジェクト。

    """
    g.params = dictutil.placeholder(g.cfg.help, m)

    help_message(m)

    m.post.ts = m.data.event_ts
    m.post.thread_title = "ヘルプメッセージ"


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
    m.status.command_type = CommandType.HELP

    g.params.update_from_dict(
        {
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
        textwrap.dedent(f"""\
        呼び出しワード：{"、".join(lookup.resolve_commands(g.params.rule_version, CommandType.SUMMARY))}
        検索範囲デフォルト：{g.cfg.summary.aggregation_range}
        """),
        StyleOptions(title="集計コマンド", indent=1, sub_title=True),
    )
    m.set_message(
        textwrap.dedent(f"""\
        呼び出しワード：{"、".join(lookup.resolve_commands(g.params.rule_version, CommandType.ANALYSIS))}
        検索範囲デフォルト：{g.cfg.analysis.aggregation_range}
        規定打数デフォルト：総対戦数 × {g.cfg.analysis.stipulated_rate} ＋ 1
        出力制限デフォルト：上位 {g.cfg.analysis.ranked} 名
        """),
        StyleOptions(title="分析コマンド", indent=1, sub_title=True),
    )
    m.set_message(
        f"呼び出しワード：{'、'.join(lookup.resolve_commands(g.params.rule_version, CommandType.MEMBER_LIST))}",
        StyleOptions(title="メンバー一覧", indent=1, sub_title=True),
    )
    m.set_message(
        f"呼び出しワード：{'、'.join(lookup.resolve_commands(g.params.rule_version, CommandType.TEAM_LIST))}",
        StyleOptions(title="チーム一覧", indent=1, sub_title=True),
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
