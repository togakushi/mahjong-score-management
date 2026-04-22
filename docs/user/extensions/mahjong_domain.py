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
            )

    def run(self) -> list[nodes.Node]:
        return super().run()


class CommonDirective(SplitWordsDescription):
    """共通オプション"""

    index_category = "common options"


class ResultsDirective(SplitWordsDescription):
    """成績サマリオプション"""

    index_category = "results options"


class GraphDirective(SplitWordsDescription):
    """成績グラフオプション"""

    index_category = "graph options"


class RankingDirective(SplitWordsDescription):
    """成績ランキングオプション"""

    index_category = "ranking options"


class ReportDirective(SplitWordsDescription):
    """成績レポートオプション"""

    index_category = "report options"


class MahjongDomain(Domain):
    """mahjong ドメイン"""

    name = "mahjong"
    label = "Mahjong"

    object_types: ClassVar[dict[str, ObjType]] = {
        "common": ObjType("common", "common"),
        "results": ObjType("results", "results"),
        "graph": ObjType("graph", "graph"),
        "ranking": ObjType("ranking", "ranking"),
        "report": ObjType("report", "report"),
    }

    directives: ClassVar[dict[str, type[Directive]]] = {
        "common": CommonDirective,
        "results": ResultsDirective,
        "graph": GraphDirective,
        "ranking": RankingDirective,
        "report": ReportDirective,
    }

    roles: ClassVar[dict[str, Any]] = {
        "common": XRefRole(),
        "results": XRefRole(),
        "graph": XRefRole(),
        "ranking": XRefRole(),
        "report": XRefRole(),
    }

    initial_data: ClassVar[dict[str, Any]] = {
        # { (objtype, name): (docname, anchor) }
        "objects": {},
    }

    # ------------------------------------------------------------------------
    def note_object(self, objtype: str, name: str, docname: str, anchor: str) -> None:
        self.data["objects"][(objtype, name)] = (docname, anchor)

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
        key = (typ, target)
        if key not in self.data["objects"]:
            return None
        docname, anchor = self.data["objects"][key]
        return make_refnode(builder, fromdocname, docname, anchor, contnode, target)

    def resolve_any_xref(
        self,
        env: Any,
        fromdocname: str,
        builder: Any,
        target: str,
        node: addnodes.pending_xref,
        contnode: nodes.Element,
    ) -> list[tuple[str, nodes.reference]]:
        results: list[tuple[str, nodes.reference]] = []
        for (objtype, name), (docname, anchor) in self.data["objects"].items():
            if name == target:
                ref = make_refnode(builder, fromdocname, docname, anchor, contnode, target)
                results.append((f"mahjong:{objtype}", ref))
        return results

    def get_objects(self) -> Any:
        for (objtype, name), (docname, anchor) in self.data["objects"].items():
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
