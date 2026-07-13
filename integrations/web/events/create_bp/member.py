"""
integrations/web/events/member.py
"""

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from flask import Blueprint, abort, current_app, render_template, request

import libs.global_value as g
from libs.commands.registry import member, team
from libs.functions import adjusting, lookup
from libs.types import StyleOptions
from libs.utils import dictutil

if TYPE_CHECKING:
    from integrations.web.adapter import ServiceAdapter


def member_bp(adapter: "ServiceAdapter") -> Blueprint:
    """
    メンバー管理ページ用Blueprint

    Args:
        adapter (ServiceAdapter): web用アダプタ

    Returns:
        Blueprint: Blueprint

    """
    bp = Blueprint("member", __name__, url_prefix="/member")

    @bp.route("/", methods=["GET", "POST"])
    def mgt_member() -> str:
        if not adapter.conf.management_member:
            abort(403)

        padding = current_app.config["padding"]
        data: dict[str, Any] = asdict(adapter.conf)

        g.params.mode = g.cfg.rule.get_mode(g.cfg.setting.default_rule)
        g.params.rule_version = g.cfg.setting.default_rule

        if request.method == "POST":
            match request.form.get("action"):
                case "add_member":
                    if name := request.form.get("member", "").strip():
                        ret = member.append(name.split()[0:2])
                        data.update(result_msg=ret)
                case "del_member":
                    if name := request.form.get("member", "").strip():
                        ret = member.remove(name.split()[0:2])
                        data.update(result_msg=ret)
                case "add_team":
                    if team_name := request.form.get("team", "").strip():
                        ret = team.append(team_name.split()[0:2])
                        data.update(result_msg=ret)
                case "del_team":
                    if team_name := request.form.get("team", "").strip():
                        ret = team.remove(team_name.split()[0:2])
                        data.update(result_msg=ret)
                case "delete_all_team":
                    ret = team.clear()
                    data.update(result_msg=ret)

            lookup.read_memberslist()

        member_df = g.params.read_data("MEMBER_INFO")
        if member_df.empty:
            data.update(member_table="<p>登録済みメンバーはいません。</p>")
        else:
            member_df = adjusting.add_units(member_df)
            member_df.rename(
                columns=dictutil.rename_dicts(
                    member_df.columns.to_list(),
                    StyleOptions(rename_type=StyleOptions.RenameType.NORMAL),
                ),
                inplace=True,
            )
            data.update(member_table=adapter.functions.to_styled_html(member_df.drop(columns=["id"]), padding))

        team_df = g.params.read_data("TEAM_INFO")
        if team_df.empty:
            data.update(team_table="<p>登録済みチームはありません。</p>")
        else:
            team_df.rename(
                columns=dictutil.rename_dicts(
                    team_df.columns.to_list(),
                    StyleOptions(rename_type=StyleOptions.RenameType.NORMAL),
                ),
                inplace=True,
            )
            data.update(team_table=adapter.functions.to_styled_html(team_df.drop(columns=["id"]), padding))

        return render_template("registry.html", **data)

    return bp
