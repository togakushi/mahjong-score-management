"""
麻雀スコア管理ドキュメント用カスタムドメイン拡張
"""

import hashlib
from typing import Any

from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


class MahjongObjectDescription(ObjectDescription):
    """カンマ区切りの単語を個別にインデックス登録する基底クラス"""

    index_category: str = "results"
    option_spec = {
        "category": directives.unchanged,
    }

    _marker_alphabet = ("\u200b", "\u200c", "\u200d", "\u2060")

    def _index_entry_name(self, part: str) -> str:
        digest = hashlib.blake2s(self.objtype.encode("utf-8"), digest_size=4).digest()
        marker = "".join(self._marker_alphabet[b & 0b11] for b in digest)
        return f"{part}{marker}"

    def _index_group_key(self) -> str:
        return f" {self.index_category}"

    def handle_signature(self, sig: str, signode) -> str:
        parts = [name.strip() for name in sig.split(",")]
        for i, name in enumerate(parts):
            signode += addnodes.desc_sig_name(name, name)
            if i < len(parts) - 1:
                signode += addnodes.desc_sig_punctuation("", ", ")
        return sig

    def add_target_and_index(self, sig: str, fullname: str, signode) -> None:
        parts = [name.strip() for name in sig.split(",")]
        domain: MahjongDomain = self.env.get_domain("mahjong")  # type: ignore[assignment]
        category = self.options.get("category", "").strip()

        if not parts:
            return

        primary_anchor = f"{self.objtype}-{parts[0]}"
        if primary_anchor not in self.state.document.ids:
            signode["ids"].append(primary_anchor)
            self.state.document.note_explicit_target(signode)

        # category 分離用に objtype ハッシュから不可視マーカーを生成する。
        # 表示文字ではないので異なるディレクティブ間で同名 category が混在しなくなる。
        digest = hashlib.blake2s(self.objtype.encode("utf-8"), digest_size=4).digest()
        objtype_marker = "".join(self._marker_alphabet[b & 0b11] for b in digest)

        for part in parts:
            if category:
                # category 表示名はそのままに、内部キーに不可視マーカーを付加して
                # 異なるディレクティブ間でのサブグループ混在を防ぐ。
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

    def run(self):
        return super().run()


class CommonDirective(MahjongObjectDescription):
    """共通オプション"""

    index_category = "common options"


class ResultsDirective(MahjongObjectDescription):
    """成績サマリオプション"""

    index_category = "results options"


class GraphDirective(MahjongObjectDescription):
    """成績グラフオプション"""

    index_category = "graph options"


class RankingDirective(MahjongObjectDescription):
    """成績ランキングオプション"""

    index_category = "ranking options"


class ReportDirective(MahjongObjectDescription):
    """成績レポートオプション"""

    index_category = "report options"


class MahjongDomain(Domain):
    """mahjong ドメイン"""

    name = "mahjong"
    label = "Mahjong"

    object_types: dict[str, ObjType] = {
        "common": ObjType("common", "common"),
        "results": ObjType("results", "results"),
        "graph": ObjType("graph", "graph"),
        "ranking": ObjType("ranking", "ranking"),
        "report": ObjType("report", "report"),
    }

    directives: dict[str, type] = {
        "common": CommonDirective,
        "results": ResultsDirective,
        "graph": GraphDirective,
        "ranking": RankingDirective,
        "report": ReportDirective,
    }

    roles: dict[str, Any] = {
        "common": XRefRole(),
        "results": XRefRole(),
        "graph": XRefRole(),
        "ranking": XRefRole(),
        "report": XRefRole(),
    }

    initial_data: dict[str, Any] = {
        # { (objtype, name): (docname, anchor) }
        "objects": {},
    }

    # ------------------------------------------------------------------------
    def note_object(self, objtype: str, name: str, docname: str, anchor: str) -> None:
        self.data["objects"][(objtype, name)] = (docname, anchor)

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        key = (typ, target)
        if key not in self.data["objects"]:
            return None
        docname, anchor = self.data["objects"][key]
        return make_refnode(builder, fromdocname, docname, anchor, contnode, target)

    def resolve_any_xref(self, env, fromdocname, builder, target, node, contnode):
        results = []
        for (objtype, name), (docname, anchor) in self.data["objects"].items():
            if name == target:
                ref = make_refnode(builder, fromdocname, docname, anchor, contnode, target)
                results.append((f"mahjong:{objtype}", ref))
        return results

    def get_objects(self):
        for (objtype, name), (docname, anchor) in self.data["objects"].items():
            yield (name, name, objtype, docname, anchor, 1)


# ----------------------------------------------------------------------------
def setup(app) -> dict[str, Any]:
    """
    _summary_

    Args:
        app (_type_): _description_

    Returns:
        dict[str, Any]: _description_
    """
    app.add_domain(MahjongDomain)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
