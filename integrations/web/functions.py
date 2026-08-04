"""
integrations/web/functions.py
"""

import re
from typing import TYPE_CHECKING, Any

from flask import make_response, render_template

from integrations.base.interface import FunctionsInterface

if TYPE_CHECKING:
    import pandas as pd
    from flask import Request, Response

    from integrations.protocols import MessageParserProtocol


class SvcFunctions(FunctionsInterface):
    """WebUI専用関数"""

    def to_styled_html(self, df: "pd.DataFrame", padding: str, index: bool = False) -> str:
        """
        データフレームをHTML表に変換

        Args:
            df (pd.DataFrame): 変換元データ
            padding (str): パディング
            index (bool): インデックスの表示

        Returns:
            str: HTML表

        """
        styled = (
            df.style.format(na_rep="-----")
            .set_table_attributes('class="data_table"')
            .set_table_styles(
                [
                    {
                        "selector": "th",
                        "props": [
                            ("color", "#ffffff"),
                            ("background-color", "#000000"),
                            ("text-align", "center"),
                            ("padding", padding),
                        ],
                    },
                    {"selector": "td", "props": [("text-align", "center"), ("padding", padding)]},
                    {"selector": "tr:nth-child(odd)", "props": [("background-color", "#f0f0f0f0")]},
                    {"selector": "tr:nth-child(even)", "props": [("background-color", "#dfdfdfdf")]},
                ]
            )
        )
        if not index:
            styled = styled.hide(axis="index")

        ret = styled.to_html()
        ret = re.sub(r" >-(\d+)</td>", r" >▲\1</td>", ret)  # 素点
        ret = re.sub(r" >-(\d+\.\d)(点?)</td>", r" >▲\1\2</td>", ret)  # 素点(小数点付き)
        ret = re.sub(r" >-(\d+\.\d)pt</td>", r" >▲\1pt</td>", ret)  # ポイント
        ret = re.sub(r" >(\d\.\d\d)0000</td>", r" >\1</td>", ret)  # 縦持ち平均順位

        return ret

    def to_text_html(self, text: str) -> str:
        """
        テキストをHTMLに変換

        Args:
            text (str): 変換元

        Returns:
            str: 返還後

        """
        ret: str = "<p>\n"
        for line in text.splitlines():
            ret += f"{line.strip()}<br>\n"
        ret += "</p>\n"

        return ret

    def header_message(self, m: "MessageParserProtocol") -> tuple[str, str]:
        """
        ヘッダ情報取得

        Args:
            m (MessageParserProtocol): メッセージデータ

        Returns:
            tuple[str, str]: 取得文字列

        """
        message = ""
        title = ""

        if m.post.headline:
            header_data, header_option = m.post.headline
            if title := header_option.title:
                message = f"<h1>{title}</h1>\n"
            if isinstance(header_data, str):
                message += f"<p>\n{header_data.replace('\n', '<br>\n')}</p>\n"

        return title, message

    def set_cookie(self, html: str, req: "Request", data: dict[str, Any]) -> "Response":
        """
        cookie保存

        Args:
            html (str): テンプレートHTML
            req (Request): Request
            data (dict[str, Any]): データ

        Returns:
            Response: Response

        """
        page = make_response(render_template(html, **data))
        if req.method == "POST":
            if req.form.get("action") == "reset":  # cookie削除
                for k in req.cookies.keys():
                    page.delete_cookie(k, path=req.path)
            else:
                for k, v in req.form.to_dict().items():
                    if k == "action":
                        continue
                    page.set_cookie(k, v, path=req.path)

        return page

    def get_cookie(self, req: "Request") -> dict[str, str]:
        """
        cookie取得

        Args:
            req (Request): Request

        Returns:
            dict[str, str]: cookieデータ

        """
        initial_value: dict[str, str] = {
            "range": "",
            "guest": "ゲストなし",
            "display": "",
            "result": "",
            "collect": "",
        }

        target_keys: list[str] = [
            "collect",
            "display",
            "guest",
            "player",
            "range",
            "result",
            "text",
        ]

        cookie_data = initial_value
        cookie_data.update(req.cookies)
        cookie_data = req.form.to_dict()

        if get_data := req.args.get("text"):
            new_text = set("{} {}".format(req.form.get("text", ""), get_data).split())
            cookie_data["text"] = " ".join(new_text)

        if req.method == "POST":
            if req.form.get("action") == "reset":
                cookie_data = initial_value
            else:
                cookie_data.pop("action")

        return {k: v for k, v in cookie_data.items() if k in target_keys}

    def get_conversations(self, m: "MessageParserProtocol") -> dict[str, Any]:
        """Abstractmethod dummy"""
        _ = m
        return {}

    def post_processing(self, m: "MessageParserProtocol") -> None:
        """Abstractmethod dummy"""
        _ = m
