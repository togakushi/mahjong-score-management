"""
integrations/discord/events/comparison.py
"""

import asyncio
import logging
from typing import TYPE_CHECKING, cast

from discord import Message
from discord.channel import TextChannel

import libs.global_value as g
from libs.domain import modify
from libs.domain.datamodels import ComparisonResults
from libs.domain.score import GameResult
from libs.functions import lookup, validator
from libs.types import ActionStatus, CommandType, RemarkDict, StyleOptions
from libs.utils import textutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

if TYPE_CHECKING:
    from integrations.discord.adapter import ServiceAdapter
    from integrations.protocols import MessageParserProtocol


def main(m: "MessageParserProtocol") -> None:
    """
    突合処理(非同期関数呼び出しラッパー)

    Args:
        m (MessageParserProtocol): メッセージデータ

    """
    asyncio.create_task(_wrapper(m))


async def _wrapper(m: "MessageParserProtocol") -> None:
    g.adapter = cast("ServiceAdapter", g.adapter)
    results = ComparisonResults(search_after=-g.adapter.conf.search_after)
    messages_list: list["MessageParserProtocol"] = []

    await search_messages(results, messages_list)
    await check_omission(results, messages_list)
    await check_remarks(results, messages_list)
    await check_total_score(results, messages_list)

    m.set_headline(results.output("headline"), StyleOptions(title=m.keyword))
    m.set_message(results.output("mismatch"), StyleOptions(title="不一致", key_title=False))
    m.set_message(results.output("missing"), StyleOptions(title="取りこぼし", key_title=False))
    m.set_message(results.output("delete"), StyleOptions(title="削除漏れ", key_title=False))
    m.set_message(results.output("remark_mod"), StyleOptions(title="メモ更新", key_title=False))
    m.set_message(results.output("remark_del"), StyleOptions(title="メモ削除", key_title=False))
    if results.invalid_score:
        m.set_message(results.output("invalid_score"), StyleOptions(title="供託残り", key_title=False))

    m.post.thread = True
    m.status.action = ActionStatus.NOTHING
    g.adapter.api.post(m)


async def search_messages(results: ComparisonResults, messages_list: list["MessageParserProtocol"]) -> None:
    """
    メッセージ全検索

    Args:
        results (ComparisonResults): 結果格納データクラス
        messages_list (list[MessageParserProtocol]): 検索結果

    """
    g.adapter = cast("ServiceAdapter", g.adapter)

    for ch in g.adapter.api.bot.get_all_channels():
        # アクセス権がないチャンネルはスキップ
        if not ch.permissions_for(ch.guild.me).read_messages:
            continue

        if isinstance(ch, TextChannel):
            channel = g.adapter.api.bot.get_channel(ch.id)
            if not isinstance(channel, TextChannel):
                continue

            logging.debug("channel: %s, after: %s", ch.name, results.after.format(ExtDt.FMT.YMDHMS))

            messages = await channel.history(after=results.after.dt, oldest_first=True).flatten()
            for message in messages:
                if not isinstance(message, Message):
                    continue
                if message.author.bot:
                    continue

                work_m = g.adapter.parser()  # 検索結果格納用
                work_m.parser(message)
                if not work_m.check_updatable:  # DB更新不可チャンネルは対象外
                    logging.debug("skip limited channel.")
                    break

                messages_list.append(work_m)


async def check_omission(results: ComparisonResults, messages_list: list["MessageParserProtocol"]) -> None:
    """
    スコア突合

    Args:
        results (ComparisonResults): 結果格納データクラス
        messages_list (list[MessageParserProtocol]): 検索結果

    """
    g.adapter = cast("ServiceAdapter", g.adapter)
    discord_score: list[GameResult] = []

    for work_m in messages_list:
        if work_m.keyword in g.keyword_dispatcher:  # コマンドキーワードはスキップ
            continue
        if detection := validator.check_score(work_m):
            score = GameResult(**detection)
            for k, v in score.to_dict().items():  # 名前の正規化
                if str(k).endswith("_name"):
                    score.set(**{k: textutil.name_replace(str(v), guest_replace=False)})
            discord_score.append(score)
            results.score_list.update({work_m.data.event_ts: work_m})
            logging.debug(score.to_text("logging"))

    db_score = lookup.search_db_score(float(results.after.format(ExtDt.FMT.TS)))

    # DISCORD -> DATABASE
    ts_list = [x.ts for x in db_score]
    for score in discord_score:
        work_m = results.score_list[score.ts]
        if score.ts in ts_list:
            target = db_score[ts_list.index(score.ts)]
            if score != target:  # 不一致(更新)
                results.mismatch.append({"before": target, "after": score})
                logging.info("mismatch: %s (%s)", score.ts, ExtDt(float(score.ts)).format(ExtDt.FMT.YMDHMS))
                logging.debug("  * discord: %s", score.to_text("detail"))
                logging.debug("  *      db: %s", target.to_text("detail"))
                modify.db_update(score, work_m)
        else:  # 取りこぼし(追加)
            results.missing.append(score)
            logging.info("missing: %s (%s)", score.ts, ExtDt(float(score.ts)).format(ExtDt.FMT.YMDHMS))
            logging.debug(score.to_text("logging"))
            modify.db_insert(score, work_m)

    # DATABASE -> DISCORD
    ts_list = [x.ts for x in discord_score]
    work_m = g.adapter.parser()
    for score in db_score:
        if score.ts not in ts_list:  # 削除漏れ
            results.delete.append(score)
            work_m.data.event_ts = score.ts
            if score.source:
                work_m.data.channel_id = score.source.replace("discord_", "")
            logging.info("delete (Only database): %s %s", ExtDt(float(score.ts)).format(ExtDt.FMT.YMDHMS), score.to_text("logging"))
            work_m.status.command_type = CommandType.COMPARISON
            modify.db_delete(work_m)


async def check_remarks(results: ComparisonResults, messages_list: list["MessageParserProtocol"]) -> None:
    """
    メモ突合

    Args:
        results (ComparisonResults): 結果格納データクラス
        messages_list (list[MessageParserProtocol]): 検索結果

    """
    g.adapter = cast("ServiceAdapter", g.adapter)
    discord_remarks: list[RemarkDict] = []
    score_list: dict[str, GameResult] = {}

    for loop_m in messages_list:
        if detection := validator.check_score(loop_m):
            score = GameResult(**detection)
            for k, v in score.to_dict().items():  # 名前の正規化
                if str(k).endswith("_name"):
                    score.set(**{k: textutil.name_replace(str(v), guest_replace=False)})
            score_list.update({loop_m.data.event_ts: score})

        if loop_m.keyword in g.cfg.rule.remarks_words:
            for name, matter in zip(loop_m.argument[0::2], loop_m.argument[1::2]):
                # 対象外のメモはスキップ
                if not float(loop_m.data.thread_ts):
                    continue  # リプライになっていない
                if loop_m.data.thread_ts not in score_list:
                    continue  # ゲーム結果に紐付かない
                pname = textutil.name_replace(str(name), guest_replace=False)
                if pname not in score_list[loop_m.data.thread_ts].to_list("name"):
                    continue  # ゲーム結果に名前がない

                discord_remarks.append(
                    {
                        "thread_ts": loop_m.data.thread_ts,
                        "event_ts": loop_m.data.event_ts,
                        "name": pname,
                        "matter": matter,
                        "source": loop_m.status.source,
                    }
                )

    db_remarks = lookup.search_db_remarks(float(results.after.format(ExtDt.FMT.TS)))

    # DISCORD -> DATABASE
    work_m = g.adapter.parser()
    work_m.status.command_type = CommandType.COMPARISON

    for remark in discord_remarks:
        if remark in db_remarks:  # 変化なし
            continue
        results.remark_mod.append(remark)

    for event_ts in {x["event_ts"] for x in results.remark_mod}:
        work_m.data.event_ts = event_ts
        modify.remarks_delete(work_m)
    modify.remarks_append(work_m, results.remark_mod)

    # DATABASE -> DISCORD
    work_remarks = [{k: str(v) for k, v in d.items() if k != "source"} for d in discord_remarks]  # sourceを除外したリスト
    for remark in db_remarks:
        check_remark = {k: str(v) for k, v in remark.items() if k != "source"}
        if check_remark not in work_remarks:  # Discordに記録なし
            results.remark_del.append(remark)
            modify.remarks_delete_compar(work_m, remark)


async def check_total_score(results: ComparisonResults, messages_list: list["MessageParserProtocol"]) -> None:
    """
    素点合計の再チェック

    Args:
        results (ComparisonResults): 結果格納データクラス
        messages_list (list[MessageParserProtocol]): 検索結果

    """
    for work_m in messages_list:
        if detection := validator.check_score(work_m):
            score = GameResult(**detection)
            for k, v in score.to_dict().items():  # 名前の正規化
                if str(k).endswith("_name"):
                    score.set(**{k: textutil.name_replace(str(v), guest_replace=False)})
            if score.deposit:
                results.invalid_score.append(score)
