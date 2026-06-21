from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


try:
    from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
    from rdflib.namespace import OWL, SKOS

    _RDFLIB_OK = True
except Exception:  # pragma: no cover - thiếu rdflib thì bỏ qua
    Graph = None  # type: ignore
    Literal = None  # type: ignore
    Namespace = None  # type: ignore
    RDF = None  # type: ignore
    RDFS = None  # type: ignore
    URIRef = None  # type: ignore
    OWL = None  # type: ignore
    SKOS = None  # type: ignore
    _RDFLIB_OK = False


DEFAULT_ENRICHED_OWL_PATH = Path("data") / "ontology" / "taxon_enriched.owl"
DEFAULT_ALIAS_ENRICHED_OWL_PATH = Path("data") / "ontology" / "taxon_enriched_aliases.owl"
DEFAULT_FACT_ENRICHED_OWL_PATH = Path("data") / "ontology" / "taxon_enriched_facts.owl"
DEFAULT_FACT_ENRICHED_V2_OWL_PATH = Path("data") / "ontology" / "taxon_enriched_facts_v2.owl"
DEFAULT_OWL_PATH = Path("data") / "ontology" / "taxon.owl"

_DISEASE_CANONICAL_REGISTRY: list[tuple[str, set[str]]] = [
    (
        "AHPND",
        {
            "ahpnd",
            "acutehepatopancreaticnecrosisdisease",
            "acutehepatopancreaticnecrosissyndrome",
            "benhhoaitugantuycap",
            "hoaitugantuycap",
        },
    ),
    (
        "IMN",
        {
            "imn",
            "imnv",
            "infectiousmyonecrosis",
            "infectiousmyonecrosisvirus",
            # Biến thể cụm từ theo tiêu đề corpus (ví dụ sổ tay FAO về IMN tôm).
            "shrimpinfectiousmyonecrosis",
            "infectiousmyonecrosisvirusimnv",
        },
    ),
    (
        "WSSV",
        {
            "wssv",
            "whitespot",
            "whitespotdisease",
            "white-spot",
        },
    ),
    (
        "vibriosis",
        {
            "vibriosis",
            "vibrio",
        },
    ),
]


def _count_document_nodes(graph: "Graph", doc_class_uri: "URIRef | None") -> int:
    """
    Đếm nút tài liệu không cần reasoner:
    - Coi là nút tài liệu nếu lớp rdf:type là Document hoặc chuỗi cha/con
      có độ sâu giới hạn nối tới Document.
    """
    if doc_class_uri is None:
        return 0
    try:
        # Lớp là subclass của doc_class_uri trong giới hạn độ sâu đã duyệt.
        doc_related_classes: set[URIRef] = set()
        for cls in graph.subjects(RDF.type, OWL.Class):
            if not isinstance(cls, URIRef):
                continue
            ancestors = _walk_superclasses(graph, cls, max_depth=12)
            if doc_class_uri in ancestors or cls == doc_class_uri:
                doc_related_classes.add(cls)

        if not doc_related_classes:
            return 0

        # Đếm individual có kiểu thuộc một trong các lớp liên quan.
        cnt = 0
        for typed_cls in doc_related_classes:
            cnt += sum(1 for _ in graph.subjects(RDF.type, typed_cls))
        return cnt
    except Exception:
        return 0


def _local_name(uri: Any) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    return s


def normalize_kg_text(text: Any) -> str:
    """
    Chuẩn hóa giống hybrid_search.normalize_text():
    - chữ thường
    - bỏ dấu tiếng Việt
    - giữ [a-z0-9 khoảng trắng ; , _ -]
    - gom khoảng trắng
    """
    if text is None:
        return ""
    try:
        # Tương thích kiểu kiểm NaN kiểu pandas mà không import pandas.
        if isinstance(text, float) and text != text:  # NaN
            return ""
    except Exception:
        pass

    s = str(text).strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"[^a-z0-9\s;,_-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def canonicalize_disease_key_from_kg_uri(kg_uri: str, kg_index: dict[str, Any]) -> str | None:
    """
    Nối URI/nhãn bệnh trong KG sang khóa chuẩn dùng khi chấm metadata.

    Trả về khóa như AHPND, IMN, WSSV, vibriosis, hoặc None nếu không biết.
    """
    uri_to_info: dict[str, dict[str, Any]] = kg_index.get("uri_to_info") or {}
    info = uri_to_info.get(str(kg_uri)) or {}

    # Chuỗi ứng viên từ chỉ mục ontology: nhãn, alias, tên local.
    candidates: list[str] = []
    if info.get("label"):
        candidates.append(str(info["label"]))
    for a in (info.get("aliases") or []):
        candidates.append(str(a))
    candidates.append(_local_name(str(kg_uri)))

    # Chuẩn hóa: bỏ khoảng trắng/dấu phân tách để khớp token trong registry.
    norm_keys: set[str] = set()
    for c in candidates:
        n = normalize_kg_text(c)
        if not n:
            continue
        n2 = n.replace(" ", "").replace("-", "").replace("_", "")
        if n2:
            norm_keys.add(n2)

    for canon, tokens in _DISEASE_CANONICAL_REGISTRY:
        if any(k in tokens for k in norm_keys):
            return canon
        # Cho phép khớp chuỗi con nếu tên bệnh nằm trong token (an toàn với các registry này).
        if any(any(t in k for t in tokens) for k in norm_keys):
            return canon
    return None


def load_kg(owl_path: str | Path) -> "Graph":
    if not _RDFLIB_OK:
        raise ImportError("rdflib is not available")

    p = Path(owl_path)
    if not p.exists():
        raise FileNotFoundError(f"OWL not found: {p}")

    g = Graph()
    # rdflib tự nhận RDF/XML từ .owl
    g.parse(str(p))
    return g


def load_kg_prefer_enriched(
    enriched_owl_path: str | Path = DEFAULT_ENRICHED_OWL_PATH,
    fallback_owl_path: str | Path = DEFAULT_OWL_PATH,
) -> tuple["Graph", str, bool]:
    """
    Ưu tiên ontology enriched, có fallback an toàn.
    Trả về: (đồ thị, đường dẫn file owl đã nạp, đã dùng enriched hay không)
    """
    enriched_p = Path(enriched_owl_path)
    fallback_p = Path(fallback_owl_path)

    if not _RDFLIB_OK:
        raise ImportError("rdflib is not available")

    errors: list[str] = []

    # Ưu tiên enriched
    try:
        if enriched_p.exists():
            g = load_kg(enriched_p)
            # Tìm lớp Document theo tên local.
            doc_class = None
            try:
                for c in g.subjects(RDF.type, OWL.Class):
                    if _local_name(str(c)) == "Document":
                        doc_class = c  # type: ignore[assignment]
                        break
            except Exception:
                doc_class = None

            if _count_document_nodes(g, doc_class) > 0:
                return g, str(enriched_p), True
            errors.append(f"enriched loaded but has 0 Document nodes (maybe invalid): {enriched_p}")
        else:
            errors.append(f"enriched OWL missing: {enriched_p}")
    except Exception as e:
        errors.append(f"failed to load enriched OWL {enriched_p}: {e}")

    # Fallback sang taxon.owl
    try:
        g2 = load_kg(fallback_p)
        return g2, str(fallback_p), False
    except Exception as e2:
        raise RuntimeError(
            "Failed to load KG ontology (enriched + fallback). Errors: " + "; ".join(errors) + f"; fallback error: {e2}"
        )


def load_kg_prefer_alias_enriched(
    alias_enriched_owl_path: str | Path = DEFAULT_ALIAS_ENRICHED_OWL_PATH,
    enriched_owl_path: str | Path = DEFAULT_ENRICHED_OWL_PATH,
    fallback_owl_path: str | Path = DEFAULT_OWL_PATH,
) -> tuple["Graph", str, str]:
    """
    Thứ tự ưu tiên:
      1) ontology alias-enriched
      2) enriched
      3) base
    Trả về: (đồ thị, đường dẫn file, nguồn) với used_source trong {"alias","enriched","base"}
    """
    alias_p = Path(alias_enriched_owl_path)
    enriched_p = Path(enriched_owl_path)
    fallback_p = Path(fallback_owl_path)

    if not _RDFLIB_OK:
        raise ImportError("rdflib is not available")

    errors: list[str] = []

    # 1) Thử alias-enriched
    try:
        if alias_p.exists():
            g_alias = load_kg(alias_p)

            doc_class = None
            try:
                for c in g_alias.subjects(RDF.type, OWL.Class):
                    if _local_name(str(c)) == "Document":
                        doc_class = c  # type: ignore[assignment]
                        break
            except Exception:
                doc_class = None

            if _count_document_nodes(g_alias, doc_class) > 0:
                return g_alias, str(alias_p), "alias"
            errors.append(f"alias enriched loaded but has 0 Document nodes (maybe invalid): {alias_p}")
        else:
            errors.append(f"alias enriched OWL missing: {alias_p}")
    except Exception as e:
        errors.append(f"failed to load alias enriched OWL {alias_p}: {e}")

    # 2) Thử enriched + fallback
    try:
        g, loaded_path, used_enriched = load_kg_prefer_enriched(enriched_p, fallback_p)
        used_source = "enriched" if used_enriched else "base"
        return g, loaded_path, used_source
    except Exception as e2:
        raise RuntimeError(
            "Failed to load KG ontology (alias-enriched + enriched + fallback). Errors: "
            + "; ".join(errors)
            + f"; last error: {e2}"
        )


def load_kg_prefer_facts_then_alias_enriched(
    facts_enriched_owl_path: str | Path = DEFAULT_FACT_ENRICHED_OWL_PATH,
    alias_enriched_owl_path: str | Path = DEFAULT_ALIAS_ENRICHED_OWL_PATH,
    enriched_owl_path: str | Path = DEFAULT_ENRICHED_OWL_PATH,
    fallback_owl_path: str | Path = DEFAULT_OWL_PATH,
) -> tuple["Graph", str, str]:
    """
    Thứ tự ưu tiên:
      1) taxon_enriched_facts_v2.owl
      2) taxon_enriched_facts.owl
      3) taxon_enriched_aliases.owl
      4) taxon_enriched.owl
      5) taxon.owl
    """
    facts_p = Path(facts_enriched_owl_path)
    facts_v2_p = Path(DEFAULT_FACT_ENRICHED_V2_OWL_PATH)
    if not _RDFLIB_OK:
        raise ImportError("rdflib is not available")

    # 1) Thử facts-enriched v2
    try:
        if facts_v2_p.exists():
            g_facts_v2 = load_kg(facts_v2_p)
            doc_class = None
            try:
                for c in g_facts_v2.subjects(RDF.type, OWL.Class):
                    if _local_name(str(c)) == "Document":
                        doc_class = c  # type: ignore[assignment]
                        break
            except Exception:
                doc_class = None
            if _count_document_nodes(g_facts_v2, doc_class) > 0:
                return g_facts_v2, str(facts_v2_p), "facts_v2"
    except Exception:
        pass

    # 2) Thử facts-enriched (v1)
    try:
        if facts_p.exists():
            g_facts = load_kg(facts_p)
            doc_class = None
            try:
                for c in g_facts.subjects(RDF.type, OWL.Class):
                    if _local_name(str(c)) == "Document":
                        doc_class = c  # type: ignore[assignment]
                        break
            except Exception:
                doc_class = None

            if _count_document_nodes(g_facts, doc_class) > 0:
                return g_facts, str(facts_p), "facts"
    except Exception:
        # File facts lỗi cú pháp/không parse được thì fallback phía dưới.
        pass

    # 3) Fallback alias-enriched (bản thân nó còn fallback enriched/base)
    g, loaded_path, used_source = load_kg_prefer_alias_enriched(
        alias_enriched_owl_path=alias_enriched_owl_path,
        enriched_owl_path=enriched_owl_path,
        fallback_owl_path=fallback_owl_path,
    )
    return g, loaded_path, used_source


def _compile_boundary_regex(alias_norm: str) -> re.Pattern:
    escaped = re.escape(alias_norm)
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])")


def _spans_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return not (a[1] <= b[0] or b[1] <= a[0])


def _select_non_overlapping_greedy(candidates: list[dict]) -> list[dict]:
    # Dài trước, rồi trái sang phải
    candidates_sorted = sorted(
        candidates,
        key=lambda x: (-(x["span"][1] - x["span"][0]), x["span"][0], x["span"][1]),
    )
    selected: list[dict] = []
    spans: list[tuple[int, int]] = []
    for c in candidates_sorted:
        if any(_spans_overlap(c["span"], s) for s in spans):
            continue
        selected.append(c)
        spans.append(c["span"])
    selected.sort(key=lambda x: x["span"][0])
    return selected


def _literal_to_str(v: Any) -> str:
    if v is None:
        return ""
    try:
        if isinstance(v, Literal):
            return str(v)
    except Exception:
        pass
    return str(v)


def _iter_literals(g: "Graph", s: "URIRef", p: "URIRef") -> Iterable[str]:
    for o in g.objects(s, p):
        yield _literal_to_str(o).strip()


def _iter_resources(g: "Graph", s: "URIRef", p: "URIRef") -> Iterable["URIRef"]:
    for o in g.objects(s, p):
        if isinstance(o, URIRef):
            yield o


def _walk_superclasses(g: "Graph", class_uri: "URIRef", max_depth: int = 10) -> set["URIRef"]:
    out: set[URIRef] = set()
    frontier = [class_uri]
    depth = 0
    while frontier and depth < max_depth:
        nxt: list[URIRef] = []
        for c in frontier:
            if c in out:
                continue
            out.add(c)
            for sup in g.objects(c, RDFS.subClassOf):
                if isinstance(sup, URIRef) and sup not in out:
                    nxt.append(sup)
        frontier = nxt
        depth += 1
    return out


@dataclass(frozen=True)
class KgEntityInfo:
    uri: str
    label: str
    entity_type: str
    aliases: tuple[str, ...]


def _guess_entity_type(g: "Graph", uri: "URIRef", ns: "Namespace") -> str:
    """
    Suy luận kiểu nhẹ không cần reasoner:
    - xem rdf:type
    - duyệt rdfs:subClassOf cho mỗi kiểu (giới hạn độ sâu)
    """
    # Các lớp đỉnh chuẩn trong ontology này
    TOP = {
        "disease": ns.Disease,
        "species": ns.Taxon,
        "location": ns.Location,
        "mode": ns.ProductionMode,
        "pathogen": ns.Pathogen,
        "symptom": ns.Symptom,
        "document": ns.Document,
        "prevention": ns.Prevention,
        "treatment": ns.Treatment,
    }

    types: list[URIRef] = [t for t in g.objects(uri, RDF.type) if isinstance(t, URIRef)]
    if not types:
        return "unknown"

    # Tiền tính bao đóng tổ tiên cho mỗi kiểu (đồ thị nhỏ nên ổn)
    ancestors: set[URIRef] = set()
    for t in types:
        ancestors |= _walk_superclasses(g, t, max_depth=12)
        ancestors.add(t)

    # Ánh xạ sang nhóm thực thể thô của ta
    for et, top_uri in TOP.items():
        if top_uri in ancestors:
            return et

    # Heuristic dự phòng: tên chứa token
    t_str = " ".join(str(t) for t in types).lower()
    if "disease" in t_str:
        return "disease"
    if "taxon" in t_str:
        return "species"
    if "location" in t_str:
        return "location"
    if "productionmode" in t_str or "mode" in t_str:
        return "mode"
    if "document" in t_str:
        return "document"
    if "pathogen" in t_str:
        return "pathogen"
    if "symptom" in t_str:
        return "symptom"
    if "prevention" in t_str:
        return "prevention"
    if "treatment" in t_str:
        return "treatment"
    return "unknown"


def build_kg_index(graph: "Graph") -> dict[str, Any]:
    if not _RDFLIB_OK:
        raise ImportError("rdflib is not available")

    ns = Namespace("http://www.semanticweb.org/lenovo/ontologies/2026/0/untitled-ontology-3#")

    REL = {
        # bệnh
        "affectsTaxon": ns.affectsTaxon,
        "causedBy": ns.causedBy,
        "hasSymptom": ns.hasSymptom,
        "recommendedPrevention": ns.recommendedPrevention,
        "recommendedTreatment": ns.recommendedTreatment,
        # loài
        "isFoundIn": ns.isFoundIn,
        "hasDisease": ns.hasDisease,
        "hasProductionMode": ns.hasProductionMode,
        # tài liệu
        "aboutDisease": ns.aboutDisease,
        "aboutTaxon": ns.aboutTaxon,
        "aboutLocation": ns.aboutLocation,
        "documentProductionMode": ns.documentProductionMode,
        "mentions": ns.mentions,
    }

    # Nguồn nhãn theo thứ tự ưu tiên
    LABEL_PROPS: list[URIRef] = [
        RDFS.label,
        SKOS.prefLabel,
        SKOS.altLabel,
        ns.scientificName,
        ns.diseaseCode,
        ns.title,
    ]

    uri_to_info: dict[str, dict[str, Any]] = {}
    label_to_entities: dict[str, list[dict[str, Any]]] = {}

    def add_alias(alias: str, uri_str: str, label: str, entity_type: str):
        a = normalize_kg_text(alias)
        if not a:
            return
        label_to_entities.setdefault(a, []).append(
            {"uri": uri_str, "label": label, "entity_type": entity_type, "alias_norm": a}
        )

    # Gom nút thực thể ứng viên: NamedIndividual + mọi chủ thể có rdf:type (kể cả URI example.org)
    subjects: set[URIRef] = set()
    for s in graph.subjects(RDF.type, OWL.NamedIndividual):
        if isinstance(s, URIRef):
            subjects.add(s)
    for s in graph.subjects(RDF.type, None):
        if isinstance(s, URIRef):
            subjects.add(s)

    for s in subjects:
        uri_str = str(s)
        et = _guess_entity_type(graph, s, ns)

        aliases: list[str] = []
        # Ưu tiên prefLabel/rdfs:label làm nhãn; không có thì lấy fragment
        label = ""

        # Thu thập alias từ các thuộc tính nhãn đã biết
        for prop in LABEL_PROPS:
            for lit in _iter_literals(graph, s, prop):
                if lit:
                    aliases.append(lit)
                    if not label and prop in {RDFS.label, SKOS.prefLabel, ns.title}:
                        label = lit

        if not label:
            # Dự phòng: fragment URI
            label = uri_str.rsplit("#", 1)[-1].replace("_", " ")

        # Khử trùng alias
        seen = set()
        aliases_uniq: list[str] = []
        for a in aliases + [label]:
            k = normalize_kg_text(a)
            if k and k not in seen:
                seen.add(k)
                aliases_uniq.append(a)

        uri_to_info[uri_str] = {
            "label": label,
            "entity_type": et,
            "aliases": aliases_uniq,
        }

        # Thêm vào chỉ mục alias
        for a in aliases_uniq:
            add_alias(a, uri_str, label, et)

    # Dựng ánh xạ doc-id (tốt nhất có thể)
    docid_to_uri: dict[str, str] = {}
    dockey_to_uri: dict[str, str] = {}

    def add_doc_key(key: str, uri_str: str):
        k = normalize_kg_text(key)
        if not k:
            return
        dockey_to_uri.setdefault(k, uri_str)

    for uri_str, info in uri_to_info.items():
        if info.get("entity_type") != "document":
            continue
        u = URIRef(uri_str)
        # Khóa mạnh: fragment local kiểu FAO_002
        frag = uri_str.rsplit("#", 1)[-1]
        add_doc_key(frag, uri_str)
        add_doc_key(frag.replace("_", " "), uri_str)

        # Khóa yếu: title / filePath
        for t in _iter_literals(graph, u, ns.title):
            add_doc_key(t, uri_str)
        for fp in _iter_literals(graph, u, ns.filePath):
            add_doc_key(fp, uri_str)
            add_doc_key(Path(fp).name, uri_str)

        # Sau này có thuộc tính định danh rõ ràng thì mở rộng tại đây.

    # Ánh xạ trực tiếp doc_id = khớp dockey đã chuẩn hóa
    for k, v in dockey_to_uri.items():
        docid_to_uri[k] = v

    # Dựng chỉ mục láng giềng cho các quan hệ quan trọng
    uri_to_neighbors: dict[str, dict[str, Any]] = {}

    def ensure_neighbors(u: str) -> dict[str, Any]:
        return uri_to_neighbors.setdefault(u, {"out": {}, "in": {}})

    important_preds = set(REL.values())
    for s, p, o in graph.triples((None, None, None)):
        if not isinstance(s, URIRef) or not isinstance(p, URIRef) or not isinstance(o, URIRef):
            continue
        if p not in important_preds:
            continue
        s_str = str(s)
        o_str = str(o)
        ensure_neighbors(s_str)["out"].setdefault(str(p), []).append(o_str)
        ensure_neighbors(o_str)["in"].setdefault(str(p), []).append(s_str)

    return {
        "ns": ns,
        "relations": {k: str(v) for k, v in REL.items()},
        "label_to_entities": label_to_entities,
        "uri_to_info": uri_to_info,
        "docid_to_uri": docid_to_uri,
        "dockey_to_uri": dockey_to_uri,
        "uri_to_neighbors": uri_to_neighbors,
    }


def link_query_entities_kg(query: str, kg_index: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """
    Khớp span regex có biên, alias dài trước, tham lam không chồng lấn.
    Nguồn alias là chỉ mục suy từ ontology (kg_index["label_to_entities"]).
    """
    q_norm = normalize_kg_text(query)
    out: dict[str, list[dict[str, Any]]] = {
        "disease": [],
        "species": [],
        "location": [],
        "mode": [],
        "pathogen": [],
        "symptom": [],
        "document": [],
        "prevention": [],
        "treatment": [],
    }
    label_to_entities: dict[str, list[dict[str, Any]]] = kg_index.get("label_to_entities") or {}
    if not q_norm or not label_to_entities:
        return out
    aliases = sorted(label_to_entities.keys(), key=lambda x: len(x), reverse=True)
    candidates: list[dict[str, Any]] = []
    for a in aliases:
        if not a:
            continue
        pat = _compile_boundary_regex(a)
        for m in pat.finditer(q_norm):
            for ent in label_to_entities.get(a, []):
                et = ent.get("entity_type") or "unknown"
                if et not in out:
                    continue
                candidates.append(
                    {
                        "uri": ent["uri"],
                        "label": ent.get("label", ""),
                        "entity_type": et,
                        "matched_alias": a,
                        "span": (m.start(), m.end()),
                    }
                )
    selected = _select_non_overlapping_greedy(candidates)
    for s in selected:
        out[s["entity_type"]].append(s)
    return out


def get_entity_neighbors(graph: "Graph", entity_uri: str) -> dict[str, list[str]]:
    """
    Láng giềng 1-hop của một URI thực thể qua các quan hệ quan trọng.
    Khóa là tên quan hệ chuẩn (ví dụ affectsTaxon).
    """
    ns = Namespace("http://www.semanticweb.org/lenovo/ontologies/2026/0/untitled-ontology-3#")
    u = URIRef(entity_uri)

    rels = {
        "affectsTaxon": ns.affectsTaxon,
        "causedBy": ns.causedBy,
        "hasSymptom": ns.hasSymptom,
        "isFoundIn": ns.isFoundIn,
        "hasDisease": ns.hasDisease,
        "aboutDisease": ns.aboutDisease,
        "aboutTaxon": ns.aboutTaxon,
        "aboutLocation": ns.aboutLocation,
        "documentProductionMode": ns.documentProductionMode,
        "recommendedPrevention": ns.recommendedPrevention,
        "recommendedTreatment": ns.recommendedTreatment,
    }

    out: dict[str, list[str]] = {k: [] for k in rels.keys()}
    for k, p in rels.items():
        for o in _iter_resources(graph, u, p):
            out[k].append(str(o))
        # Gồm cạnh vào để chứng cứ đối xứng (hữu ích cho Taxon -> Disease ngược)
        for s in graph.subjects(p, u):
            if isinstance(s, URIRef):
                out[k].append(str(s))

    # Khử trùng, giữ thứ tự
    for k, vals in out.items():
        seen = set()
        uniq = []
        for v in vals:
            if v not in seen:
                seen.add(v)
                uniq.append(v)
        out[k] = uniq
    return out


def get_document_facts(graph: "Graph", doc_uri: str) -> dict[str, list[str]]:
    ns = Namespace("http://www.semanticweb.org/lenovo/ontologies/2026/0/untitled-ontology-3#")
    u = URIRef(doc_uri)

    def res_list(p: URIRef) -> list[str]:
        return [str(o) for o in _iter_resources(graph, u, p)]

    # Nút tài liệu chứa fact trực tiếp; bệnh có phòng/trị liên quan qua aboutDisease.
    facts: dict[str, list[str]] = {
        "disease": res_list(ns.aboutDisease),
        "species": res_list(ns.aboutTaxon),
        "location": res_list(ns.aboutLocation),
        "mode": res_list(ns.documentProductionMode),
        "pathogen": [],
        "symptom": [],
        "prevention": [],
        "treatment": [],
    }

    # Bổ sung từ láng giềng bệnh (1-hop) khi tài liệu nhắc bệnh cụ thể.
    for dis in facts["disease"]:
        dn = get_entity_neighbors(graph, dis)
        facts["pathogen"].extend(dn.get("causedBy", []))
        facts["symptom"].extend(dn.get("hasSymptom", []))
        facts["prevention"].extend(dn.get("recommendedPrevention", []))
        facts["treatment"].extend(dn.get("recommendedTreatment", []))

    # Khử trùng
    for k in list(facts.keys()):
        seen = set()
        uniq = []
        for v in facts[k]:
            if v not in seen:
                seen.add(v)
                uniq.append(v)
        facts[k] = uniq

    return facts


def explain_kg_match(parts: list[str]) -> str:
    # Giữ gọn; code gọi hàm tự nối bằng "; "
    return "; ".join([p for p in parts if p])


def score_doc_with_kg(
    query_entities: dict[str, list[dict[str, Any]]],
    doc_facts: dict[str, list[str]],
    kg_index: dict[str, Any],
    graph: "Graph",
    query_text: str = "",
) -> dict[str, Any]:
    """
    Trả về:
      - kg_bonus_breakdown
      - kg_penalty_breakdown
      - kg_score
      - kg_explanation (danh sách chuỗi)
      - kg_direct_match / kg_relation_match / kg_context_match (số thực)
    """
    uri_to_info: dict[str, dict[str, Any]] = kg_index.get("uri_to_info") or {}
    def label(u: str) -> str:
        return (uri_to_info.get(u, {}) or {}).get("label") or u.rsplit("#", 1)[-1]
    def is_generic(u: str) -> bool:
        return "Generic_" in str(u)
    q = query_entities or {}
    q_dis = [e["uri"] for e in q.get("disease", [])]
    q_tax = [e["uri"] for e in q.get("species", [])]
    q_loc = [e["uri"] for e in q.get("location", [])]
    q_mode = [e["uri"] for e in q.get("mode", [])]
    q_path = [e["uri"] for e in q.get("pathogen", [])]
    q_prev = [e["uri"] for e in q.get("prevention", [])]
    q_treat = [e["uri"] for e in q.get("treatment", [])]
    q_sym = [e["uri"] for e in q.get("symptom", [])]
    doc_dis = set(doc_facts.get("disease", []))
    doc_tax = set(doc_facts.get("species", []))
    doc_loc = set(doc_facts.get("location", []))
    doc_mode = set(doc_facts.get("mode", []))
    doc_path = set(doc_facts.get("pathogen", []))
    doc_prev = set(doc_facts.get("prevention", []))
    doc_treat = set(doc_facts.get("treatment", []))
    doc_sym = set(doc_facts.get("symptom", []))
    bonus_parts: list[str] = []
    penalty_parts: list[str] = []
    expl: list[str] = []
    kg_direct = 0.0
    kg_rel = 0.0
    kg_ctx = 0.0
    disease_direct_evidence = 0.0
    disease_relation_evidence = 0.0
    # A) Khớp fact trực tiếp trên tài liệu
    for d in q_dis:
        if d in doc_dis:
            kg_direct += 0.25
            disease_direct_evidence += 0.25
            expl.append(f"KG direct match: document aboutDisease={label(d)}")
            bonus_parts.append(f"aboutDisease={label(d)} (+0.25)")
    for t in q_tax:
        if t in doc_tax:
            if is_generic(t):
                kg_direct += 0.06
                expl.append(f"KG direct match (generic): document aboutTaxon={label(t)}")
                bonus_parts.append(f"aboutTaxon(generic)={label(t)} (+0.06)")
            else:
                kg_direct += 0.20
                expl.append(f"KG direct match: document aboutTaxon={label(t)}")
                bonus_parts.append(f"aboutTaxon={label(t)} (+0.20)")
    for l in q_loc:
        if l in doc_loc:
            kg_direct += 0.10
            expl.append(f"KG direct match: document aboutLocation={label(l)}")
            bonus_parts.append(f"aboutLocation={label(l)} (+0.10)")
    for m in q_mode:
        if m in doc_mode:
            if is_generic(m):
                kg_direct += 0.04
                expl.append(f"KG direct match (generic): document documentProductionMode={label(m)}")
                bonus_parts.append(f"documentProductionMode(generic)={label(m)} (+0.04)")
            else:
                kg_direct += 0.10
                expl.append(f"KG direct match: document documentProductionMode={label(m)}")
                bonus_parts.append(f"documentProductionMode={label(m)} (+0.10)")
    # B) Khớp quan hệ 1-hop
    for d in q_dis:
        dn = get_entity_neighbors(graph, d)
        for t in dn.get("affectsTaxon", []):
            if t in doc_tax:
                kg_rel += 0.10
                disease_relation_evidence += 0.10
                expl.append(
                    f"KG relation match: {label(d)} affectsTaxon {label(t)}, and document aboutTaxon={label(t)}"
                )
                bonus_parts.append(f"{label(d)}->affectsTaxon->{label(t)} (+0.10)")
        for p in dn.get("causedBy", []):
            if p in doc_path:
                kg_rel += 0.08
                disease_relation_evidence += 0.08
                expl.append(f"KG relation match: {label(d)} causedBy {label(p)}, and document has pathogen={label(p)}")
                bonus_parts.append(f"{label(d)}->causedBy->{label(p)} (+0.08)")
    # B2) isFoundIn của taxon khớp địa điểm truy vấn với tài liệu nói về taxon đó
    q_loc_set = set(q_loc)
    if q_tax and q_loc_set:
        for t in q_tax:
            if t not in doc_tax:
                continue
            tn = get_entity_neighbors(graph, t)
            for loc in tn.get("isFoundIn", []):
                if loc in q_loc_set:
                    kg_rel += 0.12
                    expl.append(
                        f"KG relation match: {label(t)} isFoundIn {label(loc)}, query location matches species range"
                    )
                    bonus_parts.append(f"{label(t)}->isFoundIn->{label(loc)} (+0.12)")
    # C) Khớp ngữ cảnh yếu (triệu chứng/phòng/trị)
    for s in q_sym:
        if s in doc_sym:
            kg_ctx += 0.04
            expl.append(f"KG context match: document hasSymptom={label(s)}")
            bonus_parts.append(f"symptom={label(s)} (+0.04)")
    for p in q_prev:
        if p in doc_prev:
            kg_ctx += 0.05
            expl.append(f"KG context match: document recommendedPrevention={label(p)}")
            bonus_parts.append(f"prevention={label(p)} (+0.05)")
    for t in q_treat:
        if t in doc_treat:
            kg_ctx += 0.05
            expl.append(f"KG context match: document recommendedTreatment={label(t)}")
            bonus_parts.append(f"treatment={label(t)} (+0.05)")
    for p in q_path:
        if p in doc_path:
            kg_ctx += 0.06
            expl.append(f"KG context match: document pathogen={label(p)}")
            bonus_parts.append(f"pathogen={label(p)} (+0.06)")

    # D) Siết khi ưu tiên bệnh:
    if q_dis:
        has_disease_evidence = (disease_direct_evidence > 0.0) or (disease_relation_evidence > 0.0)
        if not has_disease_evidence:
            downweight = 0.25
            before_direct = kg_direct
            before_ctx = kg_ctx
            kg_direct = kg_direct * downweight
            kg_ctx = kg_ctx * downweight
            if before_direct > 0.0 or before_ctx > 0.0:
                expl.append(
                    "KG downweight: query has specific disease; non-disease evidence was reduced due to missing disease match"
                )
                bonus_parts.append(f"downweighted_non_disease_evidence (x{downweight:.2f})")
            kg_pen = 0.18
            penalty_parts.append(f"missing disease evidence (-{kg_pen:.2f})")
            expl.append("KG penalty: query has specific disease but document has no disease direct/relation evidence")
            kg_direct -= kg_pen

    # Ý định hẹp: câu có nuôi + taxon tôm hùm + địa điểm vùng vs tài liệu capture/thị trường.
    qnorm = normalize_kg_text(query_text or "")
    aquaculture_word = bool(re.search(r"(?<![a-z0-9])nuoi(?![a-z0-9])", qnorm))
    lobster_taxon = any(
        "tom_hum" in _local_name(u).lower() or "hum_bong" in _local_name(u).lower() for u in q_tax
    )
    regional_query_loc = bool(q_loc) and any(
        "khanh" in _local_name(u).lower()
        or "ven_bien" in _local_name(u).lower()
        or "ninh_thuan" in _local_name(u).lower()
        or "mien_trung" in _local_name(u).lower()
        for u in q_loc
    )
    if aquaculture_word and lobster_taxon and regional_query_loc and doc_mode:
        for m_uri in doc_mode:
            ln = _local_name(str(m_uri))
            if "CaptureFisheries" in ln:
                pen = 0.09
                kg_direct -= pen
                penalty_parts.append(f"aquaculture+regional intent vs capture fisheries mode (-{pen:.2f})")
                expl.append(
                    "KG penalty: query expresses aquaculture (nuoi) in a regional site; "
                    f"document production mode is capture/market fisheries ({ln})"
                )
                break

    kg_score = float(kg_direct + kg_rel + kg_ctx)
    return {
        "kg_direct_match": float(kg_direct),
        "kg_relation_match": float(kg_rel),
        "kg_context_match": float(kg_ctx),
        "kg_score": float(kg_score),
        "kg_bonus_breakdown": "; ".join(bonus_parts),
        "kg_penalty_breakdown": "; ".join(penalty_parts),
        "kg_explanation": expl,
    }

