"""
integrations/slack/api.py
"""

import logging
import re
import textwrap
from pathlib import PosixPath
from typing import TYPE_CHECKING, Any, cast

import pandas as pd

from integrations.base.interface import APIInterface
from libs.types import StyleOptions
from libs.utils import converter, textutil

if TYPE_CHECKING:
    from slack_sdk.web import SlackResponse
    from slack_sdk.web.client import WebClient

    from integrations.protocols import MessageParserProtocol


class AdapterAPI(APIInterface):
    """インターフェースAPI操作クラス"""

    # slack object
    appclient: "WebClient"
    """WebClient(botトークン使用)"""
    webclient: "WebClient"
    """WebClient(userトークン使用)"""

    def __init__(self) -> None:
        """Slack APIクライアント関連の初期設定を行う。"""
        super().__init__()

        try:
            from slack_sdk.errors import SlackApiError

            self.slack_api_error = SlackApiError
        except ModuleNotFoundError as err:
            raise ModuleNotFoundError(err.msg) from None

    def post(self, m: "MessageParserProtocol") -> None:
        """
        メッセージをポストする

        Args:
            m (MessageParserProtocol): メッセージデータ

        """

        def _post_header() -> None:
            res = self._call_chat_post_message(
                channel=m.data.channel_id,
                text=f"{header_title}{header_text.rstrip()}",
                thread_ts=m.reply_ts,
            )
            if res and res.status_code == 200:  # 見出しがある場合はスレッドにする
                m.post.ts = res.get("ts", "undetermined")

        if not m.in_thread:
            m.post.thread = False

        # 見出しポスト
        header_title = ""
        header_text = ""
        if m.post.headline:
            header_data, header_option = m.post.headline
            header_title = f"{header_option.print_title}\n"
            if isinstance(header_data, str):
                header_text = textwrap.indent(header_data, "\t" * header_option.indent)
        if not m.post.message:  # メッセージなし
            _post_header()
        elif not all(options.header_hidden for _, options in m.post.message):
            _post_header()

        # 本文
        options = StyleOptions()
        post_msg: list[str] = []
        for data, options in m.post.message:
            header = ""

            if isinstance(data, PosixPath) and data.exists():
                comment = textwrap.dedent(f"{options.print_title}\n{header_text.rstrip()}") if options.use_comment else ""
                self._call_files_upload(
                    channel=m.data.channel_id,
                    title=options.title,
                    file=str(data),
                    initial_comment=comment,
                    thread_ts=m.reply_ts,
                    request_file_info=False,
                )

            if isinstance(data, str):
                if options.key_title and (options.title != header_title):
                    header = options.print_title
                text_body = textwrap.indent(data.rstrip(), "\t" * options.indent)
                post_msg.append(f"{header}\n```\n{text_body}\n```\n" if options.codeblock else f"{header}\n{text_body}\n")

            if isinstance(data, pd.DataFrame):
                if options.key_title and (options.title != header_title):
                    header = options.print_title
                match options.data_kind:
                    case StyleOptions.DataKind.REMARKS_YAKUMAN | StyleOptions.DataKind.REMARKS_REGULATION | StyleOptions.DataKind.REMARKS_OTHER:
                        post_msg.extend(converter.df_to_remarks(data, options, limit=2800))
                    case StyleOptions.DataKind.STATS_LIST:
                        post_msg.extend(converter.df_to_text_table2(data, options, limit=2800))
                    case StyleOptions.DataKind.GAME_RESULTS:
                        post_msg.extend(converter.df_to_results_simple(data, options, limit=2900))
                    case StyleOptions.DataKind.GAME_RESULTS_ALL:
                        post_msg.extend(converter.df_to_results_details(data, options, limit=2600))
                    case StyleOptions.DataKind.RANKING:
                        post_msg.extend(converter.df_to_ranking(data, options, limit=2800))
                    case _:
                        post_msg.extend(converter.df_to_text_table1(data, options, max_chars=2900))

        post_msg = textutil.join_strings(post_msg, max_chars=2900)
        for msg in post_msg:
            self._call_chat_post_message(
                channel=m.data.channel_id,
                text=re.sub(r"\n\n+", "\n\n", msg.rstrip()),
                thread_ts=m.reply_ts,
            )

    def _call_chat_post_message(self, **kwargs: Any) -> "SlackResponse":
        """
        slackにメッセージをポストする

        Args:
            **kwargs (Any): Slack API chat_postMessage に渡す可変キーワード引数。

        Returns:
            SlackResponse: API response

        """
        res = cast("SlackResponse", {})
        if kwargs["thread_ts"] == "0":
            kwargs.pop("thread_ts")

        if not kwargs.get("text"):
            return res

        try:
            res = self.appclient.chat_postMessage(**kwargs)
        except self.slack_api_error as err:
            logging.error("slack_api_error: %s", err)
            logging.error("kwargs=%s", kwargs)

        return res

    def _call_files_upload(self, **kwargs: Any) -> "SlackResponse":
        """
        slackにファイルをアップロードする

        Args:
            **kwargs (Any): Slack API files_upload_v2 に渡す可変キーワード引数。

        Returns:
            SlackResponse | Any: API response

        """
        res = cast("SlackResponse", {})
        if kwargs.get("thread_ts", "0") == "0":
            kwargs.pop("thread_ts")

        try:
            res = self.appclient.files_upload_v2(**kwargs)
        except self.slack_api_error as err:
            logging.error("slack_api_error: %s", err)
            logging.error("kwargs=%s", kwargs)

        return res
