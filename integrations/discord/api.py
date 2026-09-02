"""
integrations/discord/api.py
"""

import asyncio
import sys
import textwrap
from pathlib import PosixPath
from typing import TYPE_CHECKING, Union, cast

import pandas as pd
from table2ascii import PresetStyle, table2ascii

import integrations.discord.events.audioop as _audioop
from integrations.base.interface import APIInterface
from libs.types import StyleOptions
from libs.utils import converter, textutil
from libs.utils.timekit import ExtendedDatetime as ExtDt

sys.modules["audioop"] = _audioop

if TYPE_CHECKING:
    from discord import ApplicationContext, Bot, Message

    from integrations.protocols import MessageParserProtocol


class AdapterAPI(APIInterface):
    """インターフェースAPI操作クラス"""

    bot: "Bot"

    def __init__(self) -> None:
        """Discord APIラッパーで利用する依存オブジェクトを初期化する。"""
        super().__init__()

        from discord import File as discord_file

        self.discord_file = discord_file

        # discord object
        self.response: Union["Message", "ApplicationContext"]

    def post(self, m: "MessageParserProtocol") -> None:
        """
        メッセージをポストする（非同期処理ラッパー）

        Args:
            m (MessageParserProtocol): メッセージデータ

        """
        if m.status.command_flg:
            asyncio.create_task(self.command_respond(m))
        else:
            asyncio.create_task(self.post_async(m))

    async def post_async(self, m: "MessageParserProtocol") -> None:
        """
        メッセージをポストする

        Args:
            m (MessageParserProtocol): メッセージデータ

        """
        self.response = cast("Message", self.response)

        if not m.in_thread:
            m.post.thread = False

        # 見出しポスト
        header_title = ""
        header_text = ""
        if m.post.headline:
            header_data, header_option = m.post.headline
            header_title = f"{header_option.print_title}"
            if isinstance(header_data, str):
                header_text = textwrap.indent(header_data, "\t" * header_option.indent)
            m.post.thread_title = header_title
        if not m.post.message:
            thread_msg = await self.response.reply(f"{header_title}\n{header_text.rstrip()}")
            m.post.thread = True
        elif not all(options.header_hidden for _, options in m.post.message):
            thread_msg = await self.response.reply(f"{m.post.thread_title}\n{header_text.rstrip()}")
            m.post.thread = True
        elif m.post.thread_title:
            thread_msg = self.response
            m.post.thread = True

        # 本文
        options = StyleOptions()
        post_msg: list[str] = []
        for data, options in m.post.message:
            header = ""

            if isinstance(data, PosixPath) and data.exists():
                comment = textwrap.dedent(f"{header_title}\n{header_text.rstrip()}") if options.use_comment else ""
                file = self.discord_file(
                    str(data),
                    description=comment,
                )
                asyncio.create_task(self.response.channel.send(file=file))

            if isinstance(data, str):
                if options.key_title and (options.title != header_title):
                    header = f"{options.print_title}"
                message_text = textwrap.indent(data.rstrip().replace("<@>", f"<@{self.response.author.id}>"), "\t" * options.indent)
                post_msg.append(f"{header}\n```\n{message_text}\n```\n" if options.codeblock else f"{header}\n{message_text}\n")

            if isinstance(data, pd.DataFrame):
                if options.key_title and (options.title != header_title):
                    header = f"** {options.print_title} **"
                match options.data_kind:
                    case StyleOptions.DataKind.REMARKS_YAKUMAN | StyleOptions.DataKind.REMARKS_REGULATION | StyleOptions.DataKind.REMARKS_OTHER:
                        post_msg.extend(converter.df_to_remarks(data, options, limit=1500))
                    case StyleOptions.DataKind.STATS_LIST:
                        post_msg.extend(converter.df_to_text_table2(data, options, limit=2000))
                    case StyleOptions.DataKind.GAME_RESULTS:
                        post_msg.extend(converter.df_to_results_simple(data, options, limit=1200))
                    case StyleOptions.DataKind.GAME_RESULTS_ALL:
                        post_msg.extend(converter.df_to_results_details(data, options, limit=1200))
                    case StyleOptions.DataKind.RANKING:
                        post_msg.extend(converter.df_to_ranking(data, options, limit=1800))
                    case _:
                        post_msg.extend(converter.df_to_text_table1(data, options, limit=1900))

        post_msg = textutil.join_strings(post_msg, limit=1900)
        if thread_msg and m.post.thread:
            date_suffix = ExtDt(float(m.data.event_ts)).format(ExtDt.FMT.YMDHMS, ExtDt.DEM.SLASH)
            if not m.post.thread_title.isnumeric() and m.post.thread_title:
                thread = await thread_msg.create_thread(name=f"{m.post.thread_title} - {date_suffix}")
                for msg in post_msg:
                    for split_msg in textutil.split_strings(msg, limit=1800):
                        await thread.send(split_msg)
            else:  # 数字タイトルはスレッドにしない
                for msg in post_msg:
                    for split_msg in textutil.split_strings(msg, limit=1800):
                        await self.response.reply(split_msg)
        else:
            for msg in post_msg:
                for split_msg in textutil.split_strings(msg, limit=1800):
                    await self.response.reply(split_msg)

    async def command_respond(self, m: "MessageParserProtocol") -> None:
        """
        スラッシュコマンド応答

        Args:
            m (MessageParserProtocol): メッセージデータ

        """
        self.response = cast("ApplicationContext", self.response)

        for data, options in m.post.message:
            if isinstance(data, PosixPath) and data.exists():
                file = self.discord_file(str(data))
                await self.response.send(file=file)

            if isinstance(data, str):
                if options.codeblock:
                    data = f"```\n{data}\n```"
                await self.response.respond(data)

            if isinstance(data, pd.DataFrame):
                output = table2ascii(
                    header=data.columns.to_list(),
                    body=data.to_dict(orient="split")["data"],
                    style=PresetStyle.ascii_borderless,
                )
                await self.response.respond(f"```\n{output}\n```")
