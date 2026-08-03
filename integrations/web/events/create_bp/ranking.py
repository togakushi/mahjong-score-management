"""
integrations/web/events/ranking.py
"""

from dataclasses import asdict
from typing import TYPE_CHECKING

import pandas as pd
from flask import Blueprint, abort, current_app, request

import libs.dispatcher
from libs.functions import adjusting
from libs.types import StyleOptions
from libs.utils import dictutil

if TYPE_CHECKING:
    from flask import Response

    from integrations.web.adapter import ServiceAdapter


def ranking_bp(adapter: "ServiceAdapter") -> Blueprint:
    """
    ランキングページ用Blueprint

    Args:
        adapter (ServiceAdapter): web用アダプタ

    Returns:
        Blueprint: Blueprint

    """
    bp = Blueprint("ranking", __name__, url_prefix="/ranking")

    @bp.route("/", methods=["GET", "POST"])
    def ranking() -> "Response":
        if not adapter.conf.view_ranking:
            abort(403)

        padding = current_app.config["padding"]

        m = adapter.parser()
        cookie_data = adapter.functions.get_cookie(request)
        text = " ".join(cookie_data.values())
        m.data.text = f"{current_app.config['analysis']} {text}"
        libs.dispatcher.by_keyword(m)

        _, message = adapter.functions.header_message(m)

        for data, options in m.post.message:
            if options.title and options.key_title:
                message += f"<h2>{options.title}</h2>\n"

            if isinstance(data, pd.DataFrame):
                if options.data_kind == StyleOptions.DataKind.SCORE_ANALYSIS:
                    data.reset_index(inplace=True)
                    show_index = False
                else:
                    show_index = options.show_index
                data = adjusting.add_units(data)
                data.rename(
                    columns=dictutil.rename_dicts(
                        data.columns.to_list(),
                        StyleOptions(rename_type=StyleOptions.RenameType.NORMAL),
                    ),
                    inplace=True,
                )
                message += adapter.functions.to_styled_html(data, padding, show_index)

            if isinstance(data, str):
                message += adapter.functions.to_text_html(data)

        cookie_data.update(body=message, **asdict(adapter.conf))
        page = adapter.functions.set_cookie("ranking.html", request, cookie_data)

        return page

    return bp
