"""
libs/dispatcher.py
"""

import logging
from typing import TYPE_CHECKING

import libs.global_value as g
from integrations import factory
from libs.domain import modify
from libs.domain.score import GameResult
from libs.functions import lookup, message, validator
from libs.types import MessageStatus, StyleOptions
from libs.utils import dictutil, textutil

if TYPE_CHECKING:
    from integrations.protocols import MessageParserProtocol


def by_keyword(m: "MessageParserProtocol") -> None:
    """メイン処理"""
    g.params.default_reset()
    g.params.update_from_dict(
        {
            "database_file": g.cfg.setting.database_file,
            "logging_verbose": g.args.verbose,
        }
    )

    # ショートカット置き換え
    if shortcut := g.cfg.shortcut.get(m.keyword):
        m.data.text = m.data.text.replace(m.keyword, shortcut)

    logging.debug("keyword=%s, argument=%s, source=%s", m.keyword, m.argument, m.status.source)
    logging.debug(
        "status=%s, event_ts=%s, thread_ts=%s, in_thread=%s, is_command=%s, user_id=%s,",
        m.data.status.value,
        m.data.event_ts,
        m.data.thread_ts,
        m.in_thread,
        m.is_command,
        m.data.user_id,
    )

    # 変更がないイベントは処理をスキップ
    if m.data.status == MessageStatus.DO_NOTHING:
        return

    # 許可されていないユーザのコマンドは処理しない
    if m.ignore_user:
        logging.debug("event skip[ignore user]: %s", m.data.user_id)
        return

    # メッセージが削除された場合
    if m.data.status == MessageStatus.DELETED:
        message_deleted(m)
        return

    match m.keyword:
        # キーワード実行
        case word if word in g.keyword_dispatcher and not m.is_command:
            logging.debug("dispatch keyword")
            if m.data.status == MessageStatus.APPEND:
                g.keyword_dispatcher[word](m)
        # コマンド実行
        case word if word in g.command_dispatcher and m.is_command:
            logging.debug("dispatch command")
            if m.data.status == MessageStatus.APPEND:
                g.command_dispatcher[word](m)
        # リマインダ実行
        case "Reminder:":
            logging.debug("dispatch keyword for reminder")
            if m.data.text in g.keyword_dispatcher and m.is_bot:
                g.keyword_dispatcher[m.data.text](m)
        # その他(ディスパッチテーブルにない場合)
        case _ as word:
            logging.debug("dispatch other words")
            other_words(word, m)

    m.delete_items(dictutil.dropitems_list())
    g.adapter.api.post(m)


def other_words(word: str, m: "MessageParserProtocol") -> None:
    """
    コマンド以外のワードの処理

    Args:
        word (str): 入力ワード
        m (MessageParserProtocol): メッセージデータ

    """
    if word in g.cfg.rule.remarks_words and m.in_thread:  # 追加メモ
        if lookup.exsist_record(m.data.thread_ts).has_valid_data():
            modify.check_remarks(m)
    else:  # スコア登録
        if detection_dict := validator.check_score(m):  # 結果報告フォーマットに一致するポストの処理
            score = GameResult(**detection_dict)
            # 名前ブレ修正
            for k, p in score.to_dict().items():
                if k.endswith("_name"):
                    score.set(**{k: textutil.name_replace(str(p), guest_replace=False)})
                    continue

            match m.data.status:
                case MessageStatus.APPEND:
                    message_append(score, m)
                case MessageStatus.CHANGED:
                    message_changed(score, m)
                case _:
                    pass
        else:
            record_data = lookup.exsist_record(m.data.event_ts)
            if record_data and m.data.status == MessageStatus.CHANGED:
                message_deleted(m)


def message_append(detection: GameResult, m: "MessageParserProtocol") -> None:
    """
    メッセージの追加処理

    Args:
        detection (GameResult): スコアデータ
        m (MessageParserProtocol): メッセージデータ

    """
    if _thread_check(m):
        modify.db_insert(detection, m)
    else:
        m.post.ts = m.data.event_ts
        m.set_message(message.random_reply(m, "inside_thread"), StyleOptions(key_title=False))
        logging.debug("skip (inside thread). event_ts=%s, thread_ts=%s", m.data.event_ts, m.data.thread_ts)


def message_changed(detection: GameResult, m: "MessageParserProtocol") -> None:
    """
    メッセージの変更処理

    Args:
        detection (GameResult): スコアデータ
        m (MessageParserProtocol): メッセージデータ

    """
    record_data = lookup.exsist_record(m.data.event_ts)

    # 変更がない場合は終了
    if detection.to_dict() == record_data.to_dict():
        return

    # スレッド内チェック → 処理対象外なら終了
    if not _thread_check(m):
        m.post.ts = m.data.event_ts
        m.set_message(message.random_reply(m, "inside_thread"), StyleOptions(key_title=False))
        logging.debug("skip (inside thread). event_ts=%s, thread_ts=%s", m.data.event_ts, m.data.thread_ts)
        return

    # 既存データなし → 新規挿入
    if not record_data.has_valid_data():
        modify.db_insert(detection, m)
        modify.reprocessing_remarks(m)
        return

    # 全条件クリア → 更新実行
    modify.db_update(detection, m)


def message_deleted(m: "MessageParserProtocol") -> None:
    """
    メッセージの削除処理

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    if m.keyword in g.cfg.rule.remarks_words:  # 追加メモ
        modify.remarks_delete(m)
    else:
        modify.db_delete(m)


def _thread_check(m: "MessageParserProtocol") -> bool:
    """スレッド内判定関数"""
    if isinstance(g.adapter, factory.slack_adapter):  # type: ignore[attr-defined]
        if not m.in_thread or (m.in_thread == g.adapter.conf.thread_report):
            return True
        return False
    return not m.in_thread
