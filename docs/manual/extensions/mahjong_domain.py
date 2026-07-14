"""
Mahjong score management tool ドキュメント用カスタムドメイン拡張
"""

import hashlib
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


class SplitWordsDescription(ObjectDescription[Any]):
    """カンマ区切りの単語を個別にインデックス登録する基底クラス"""

    index_category: str = "results"
    option_spec: ClassVar[dict[str, Any]] = {
        "category": directives.unchanged,
    }

    _marker_alphabet: ClassVar[tuple[str, str, str, str]] = ("\u200b", "\u200c", "\u200d", "\u2060")

    def _index_entry_name(self, part: str) -> str:
        digest = hashlib.blake2s(self.objtype.encode("utf-8"), digest_size=4).digest()
        marker = "".join(self._marker_alphabet[b & 0b11] for b in digest)
        return f"{part}{marker}"

    def _index_group_key(self) -> str:
        return f" {self.index_category}"

    def handle_signature(self, sig: str, signode: addnodes.desc_signature) -> str:
        parts = [name.strip() for name in sig.split(",")]
        for i, name in enumerate(parts):
            signode += addnodes.desc_sig_name(name, name)
            if i < len(parts) - 1:
                signode += addnodes.desc_sig_punctuation("", ", ")
        return sig

    def add_target_and_index(self, name: Any, sig: str, signode: addnodes.desc_signature) -> None:
        parts = [name.strip() for name in sig.split(",")]
        domain: MahjongDomain = self.env.get_domain("mahjong")  # type: ignore[assignment]
        category = self.options.get("category", "").strip()

        if not parts:
            return

        primary_anchor = f"{self.objtype}-{parts[0]}"
        if primary_anchor not in self.state.document.ids:
            signode["ids"].append(primary_anchor)
            self.state.document.note_explicit_target(signode)

        digest = hashlib.blake2s(self.objtype.encode("utf-8"), digest_size=4).digest()
        objtype_marker = "".join(self._marker_alphabet[b & 0b11] for b in digest)

        for part in parts:
            if category:
                category_key = f"{category}{objtype_marker}"
                entry_name = f"{category_key}; {self._index_entry_name(part)}"
                self.indexnode["entries"].append(("single", entry_name, primary_anchor, "", self._index_group_key()))
            else:
                self.indexnode["entries"].append(("single", self._index_entry_name(part), primary_anchor, "", self._index_group_key()))

            # ドメインのオブジェクト一覧に登録
            domain.note_object(
                objtype=self.objtype,
                name=part,
                docname=self.env.docname,
                anchor=primary_anchor,
                category=category or None,
            )

    def run(self) -> list[nodes.Node]:
        return super().run()


# ---
class CommonDirective(SplitWordsDescription):
    """共通オプション"""

    index_category = "共通オプション"


class SummaryDirective(SplitWordsDescription):
    """集計コマンドオプション"""

    index_category = "集計コマンドオプション"


class AnalysisDirective(SplitWordsDescription):
    """分析コマンドオプション"""

    index_category = "分析コマンドオプション"


# ---
class SettingSectionDirective(SplitWordsDescription):
    """settingセクション"""

    index_category = "setting section"


class IntegrationsSectionDirective(SplitWordsDescription):
    """integrationsセクション"""

    index_category = "integrations section"


class RuleSetSectionDirective(SplitWordsDescription):
    """rule_setセクション"""

    index_category = "rule_set section"


class RegulationsSectionDirective(SplitWordsDescription):
    """regulationsセクション"""

    index_category = "regulations section"


class AliasSectionDirective(SplitWordsDescription):
    """aliasセクション"""

    index_category = "alias section"


class MemberConfigDirective(SplitWordsDescription):
    """memberセクション"""

    index_category = "member section"


class TeamConfigDirective(SplitWordsDescription):
    """teamセクション"""

    index_category = "team section"


class DegreeSectionDirective(SplitWordsDescription):
    """degreeセクション"""

    index_category = "degree section"


class StatusSectionDirective(SplitWordsDescription):
    """statusセクション"""

    index_category = "status section"


class GradeSectionDirective(SplitWordsDescription):
    """gradeセクション"""

    index_category = "grade section"


class CustomMessageSectionDirective(SplitWordsDescription):
    """custom_messageセクション"""

    index_category = "custom_message section"


class SubCommandsSectionDirective(SplitWordsDescription):
    """sub_commandsセクション"""

    index_category = "sub_commands section"


# ---
class MahjongDomain(Domain):
    """mahjong ドメイン"""

    name = "mahjong"
    label = "Mahjong"

    object_types: ClassVar[dict[str, ObjType]] = {
        # section
        "setting_section": ObjType("setting_section", "setting_section"),
        "summary_section": ObjType("summary_section", "setting_section"),
        "analysis_section": ObjType("analysis_section", "setting_section"),
        "integrations_section": ObjType("integrations_section", "integrations_section"),
        "rule_set_section": ObjType("rule_set_section", "rule_set_section"),
        "regulations_section": ObjType("regulations_section", "regulations_section"),
        "alias_section": ObjType("alias_section", "alias_section"),
        "member_section": ObjType("member_section", "member_section"),
        "team_section": ObjType("team_section", "team_section"),
        "degree_section": ObjType("degree_section", "degree_section"),
        "status_section": ObjType("status_section", "status_section"),
        "grade_section": ObjType("grade_section", "grade_section"),
        "custom_message_section": ObjType("custom_message_section", "custom_message_section"),
        "sub_commands_section": ObjType("sub_commands_section", "sub_commands_section"),
        # option
        "common": ObjType("common", "common"),
        "summary": ObjType("summary", "summary"),
        "analysis": ObjType("analysis", "analysis"),
    }

    directives: ClassVar[dict[str, type[Directive]]] = {
        # section
        "setting_section": SettingSectionDirective,
        "integrations_section": IntegrationsSectionDirective,
        "rule_set_section": RuleSetSectionDirective,
        "regulations_section": RegulationsSectionDirective,
        "alias_section": AliasSectionDirective,
        "member_section": MemberConfigDirective,
        "team_section": TeamConfigDirective,
        "degree_section": DegreeSectionDirective,
        "status_section": StatusSectionDirective,
        "grade_section": StatusSectionDirective,
        "custom_message_section": CustomMessageSectionDirective,
        "sub_commands_section": SubCommandsSectionDirective,
        # option
        "common": CommonDirective,
        "summary": SummaryDirective,
        "analysis": AnalysisDirective,
    }

    roles: ClassVar[dict[str, Any]] = {
        # section
        "setting_section": XRefRole(),
        "integrations_section": XRefRole(),
        "rule_set_section": XRefRole(),
        "regulations_section": XRefRole(),
        "alias_section": XRefRole(),
        "member_section": XRefRole(),
        "team_section": XRefRole(),
        "degree_section": XRefRole(),
        "status_section": XRefRole(),
        "grade_section": XRefRole(),
        "custom_message_section": XRefRole(),
        "sub_commands_section": XRefRole(),
        # option
        "common": XRefRole(),
        "summary": XRefRole(),
        "analysis": XRefRole(),
    }

    initial_data: ClassVar[dict[str, Any]] = {
        # { (objtype, category, name): (docname, anchor) }
        "objects": {},
    }

    @staticmethod
    def _split_target(target: str) -> tuple[str | None, str]:
        normalized = target.replace("；", ";")
        if ";" not in normalized:
            return None, normalized.strip()
        category, name = normalized.split(";", 1)
        return category.strip(), name.strip()

    # ------------------------------------------------------------------------
    def note_object(self, objtype: str, name: str, docname: str, anchor: str, category: str | None = None) -> None:
        self.data["objects"][(objtype, category, name)] = (docname, anchor)

    def resolve_xref(
        self,
        env: Any,
        fromdocname: str,
        builder: Any,
        typ: str,
        target: str,
        node: addnodes.pending_xref,
        contnode: nodes.Element,
    ) -> nodes.reference | None:
        category, name = self._split_target(target)

        if category is not None:
            key_with_category = (typ, category, name)
            if key_with_category not in self.data["objects"]:
                return None
            docname, anchor = self.data["objects"][key_with_category]
            return make_refnode(builder, fromdocname, docname, anchor, contnode, name)

        key_without_category = (typ, None, name)
        if key_without_category in self.data["objects"]:
            docname, anchor = self.data["objects"][key_without_category]
            return make_refnode(builder, fromdocname, docname, anchor, contnode, name)

        matches = [value for (objtype, _category, objname), value in self.data["objects"].items() if objtype == typ and objname == name]
        if len(matches) == 1:
            docname, anchor = matches[0]
            return make_refnode(builder, fromdocname, docname, anchor, contnode, name)
        return None

    def resolve_any_xref(
        self,
        env: Any,
        fromdocname: str,
        builder: Any,
        target: str,
        node: addnodes.pending_xref,
        contnode: nodes.Element,
    ) -> list[tuple[str, nodes.reference]]:
        category, name = self._split_target(target)
        results: list[tuple[str, nodes.reference]] = []
        for (objtype, item_category, item_name), (docname, anchor) in self.data["objects"].items():
            if item_name != name:
                continue
            if category is not None and item_category != category:
                continue
            ref = make_refnode(builder, fromdocname, docname, anchor, contnode, name)
            results.append((f"mahjong:{objtype}", ref))
        return results

    def get_objects(self) -> Any:
        for (objtype, _category, name), (docname, anchor) in self.data["objects"].items():
            yield (name, name, objtype, docname, anchor, 1)


# ----------------------------------------------------------------------------
def setup(app: Sphinx) -> dict[str, Any]:
    """
    Mahjong score management tool 用カスタムドメインの登録

    Args:
        app (Sphinx): 拡張登録先の Sphinx アプリケーションインスタンス

    Returns:
        dict[str, Any]: 拡張のメタ情報（バージョンと並列ビルド可否）
    """
    app.add_domain(MahjongDomain)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
