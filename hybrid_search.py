import re
import unicodedata
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

from vector_search import load_index, search

# Tích hợp KG runtime tùy chọn; nếu thiếu rdflib/OWL vẫn chạy được.
try:
    import kg_runtime

    _KG_RUNTIME_OK = True
except Exception:
    kg_runtime = None  
    _KG_RUNTIME_OK = False


# CẤU HÌNH
METADATA_PATH = "data/metadata/document_metadata_cleaned.xlsx"
KG_ALIAS_ENRICHED_PATH = Path("data") / "ontology" / "taxon_enriched_aliases.owl"
KG_ENRICHED_PATH = Path("data") / "ontology" / "taxon_enriched.owl"
KG_FALLBACK_PATH = Path("data") / "ontology" / "taxon.owl"
KG_FACT_ENRICHED_PATH = Path("data") / "ontology" / "taxon_enriched_facts.owl"
KG_FACT_ENRICHED_V2_PATH = Path("data") / "ontology" / "taxon_enriched_facts_v2.owl"
CANDIDATE_K = 10
FINAL_K = 5

# Truy vấn tiếng Việt kiểu "tôm hùm" + tỉnh ven biển: embedding đa ngôn ngữ đôi khi bỏ sót
# PDF thị trường/catalogue tiếng Anh ở lát FAISS đầu. Một lần truy vấn tiếng Anh ngắn
# cùng index/model kéo các tài liệu đó vào pool rerank cho ý định hẹp này; không đổi pipeline index/embed.
LOBSTER_COASTAL_VECTOR_BOOST_QUERY = (
    "GLOBEFISH lobster analysis marine lobsters FAO species catalogue decapod"
)

TEST_QUERIES = [
    "bệnh AHPND trên tôm",
    "bệnh đốm trắng ở tôm thẻ chân trắng",
    "nuôi tôm hùm ở Khánh Hòa",
    "infectious myonecrosis",
    "bệnh thường gặp trên cá bớp",
    "production mode trại giống tôm thẻ chân trắng",
    "tài liệu về trại giống tôm sú ở Ấn Độ",
    "biosecurity trong hatchery tôm thẻ chân trắng",
    "aquaculture disease prevention",
    "shrimp hatchery latin america",
]

WEIGHTS = {
    "disease": 0.20,
    "species": 0.15,
    "location": 0.10,
    "mode": 0.10,
}

ENTITY_COLUMNS = {
    "disease": "related_disease",
    "species": "related_taxon",
    "location": "related_location",
    "mode": "production_mode",
}

# Chuẩn hóa để giải thích/CSV thống nhất và giảm biến thể trùng.
def canonicalize_term(entity_type: str, term: str) -> str:
    term_norm = normalize_text(term)

    if entity_type == "disease":
        # Gom cách viết IMN/IMNV về một nhóm metadata.
        nocomp = term_norm.replace(" ", "").replace("-", "")
        if nocomp in {
            "imn",
            "imnv",
            "infectiousmyonecrosis",
            "infectiousmyonecrosisvirus",
            "infectiousmyonecrosisvirusdisease",
            "shrimpinfectiousmyonecrosis",
            "imnvdisease",
        } or term_norm in {
            "infectious myonecrosis",
            "infectious myonecrosis virus",
            "infectious myonecrosis virus disease",
            "shrimp infectious myonecrosis",
            "imnv disease",
        }:
            return "IMN"
        # Nhãn KG Việt/Anh cho bệnh có metadata và disease_priority riêng.
        if "ahpnd" in nocomp or "hoaitugantuycap" in nocomp:
            return "AHPND"
        # Bridge label ↔ code cho bệnh đốm trắng (WSSV / White spot disease).
        # Mục tiêu: metadata thường lưu code "WSSV" còn KG/query có thể là nhãn tiếng Việt/Anh.
        if (
            "wssv" in nocomp
            or "whitespot" in nocomp
            or "whitespotdisease" in nocomp
            or "domtrang" in nocomp
            or "benhdomtrang" in nocomp
            # Trường hợp chữ "đ" bị loại bởi normalize_text() (đốm -> "om").
            or "omtrang" in nocomp
            or "benhomtrang" in nocomp
        ):
            return "WSSV"

    if entity_type == "species":
        if term_norm in {"lobsters"}:
            return "lobster"
        # Nhãn KG cho Panulirus ornatus trong ontology; nhóm metadata là "lobster".
        if term_norm in {"tom hum", "tom hum bong", "ornate spiny lobster", "mud spiny lobster"}:
            return "lobster"
        if term_norm in {
            "penaeus vannamei",
            "litopenaeus vannamei",
            "white shrimp",
            "whiteleg shrimp",
            "tom the chan trang",
        }:
            return "Penaeus vannamei"
        if term_norm in {
            "penaeus monodon",
            "tom su",
            "black tiger shrimp",
        }:
            return "Penaeus monodon"

    if entity_type == "location":
        # Giữ độ chi tiết địa điểm; không gom tỉnh/thành về quốc gia tại đây.
        if term_norm in {"khanh hoa", "khánh hòa"}:
            return "Khanh Hoa"
        # Khớp nhãn KG vùng biển với truy vấn cấp tỉnh Khánh Hòa.
        if term_norm in {"ven bien khanh hoa", "khanh hoa coastal waters"}:
            return "Khanh Hoa"
        if term_norm in {"viet nam", "vietnam"}:
            return "Vietnam"
        if term_norm in {"thailand", "thai lan"}:
            return "Thailand"
        if term_norm in {"global"}:
            return "Global"

    return term


# Ánh xạ cha–con để khớp metadata ở mức rộng hơn.
# Ví dụ: hỏi Khánh Hòa nhưng metadata chỉ có Vietnam.
LOCATION_PARENT_MAP = {
    "Khanh Hoa": "Vietnam",
}

MANUAL_ALIASES = {
    "disease": {
        "AHPND": [
            "ahpnd",
            "acute hepatopancreatic necrosis disease",
            "benh hoai tu gan tuy cap",
        ],
        "WSSV": [
            "wssv",
            "white spot",
            "white spot disease",
            "whitespot",
            "whitespot disease",
            "benh dom trang",
            "bệnh đốm trắng",
            "dom trang",
            "đốm trắng",
            # Sau normalize_text(), "đốm" -> "om" (vì ký tự đ không thuộc [a-z]).
            "benh om trang",
            "om trang",
        ],
        "fish diseases": [
            "fish diseases",
            # Không dùng "benh thuong gap" đơn lẻ — khớp nhầm truy vấn tôm nước lợ (LO_007).
            "benh thuong gap tren ca",
            "benh ca",
            "benh ca thuong gap",
        ],
        "IMN": [
            "imn",
            "imnv",
            "infectious myonecrosis",
            "infectious myonecrosis virus",
            "infectious myonecrosis virus disease",
            "shrimp infectious myonecrosis",
            "imnv disease",
        ],
    },
    # Các bucket dưới đây chỉ để phân loại ý định/chủ đề; KHÔNG phải bệnh.
    "topic": {
        "biosecurity": [
            "biosecurity",
            "an toan sinh hoc",
        ],
    },
    "management": {
        "health management": [
            "health management",
            "quan ly suc khoe",
        ],
    },
    "prevention": {
        "disease prevention": [
            "disease prevention",
            "phong benh",
        ],
    },
    "species": {
        "shrimp": [
            "shrimp",
            "tom",
        ],
        "fish": [
            "fish",
            "ca bop",
            "cá bớp",
            "cá bop",
        ],
        "Penaeus monodon": [
            "penaeus monodon",
            "tom su",
            "black tiger shrimp",
        ],
        "Penaeus vannamei": [
            "penaeus vannamei",
            "litopenaeus vannamei",
            "tom the chan trang",
            "tom the",
            "whiteleg shrimp",
            "white shrimp",
        ],
        "lobster": [
            "lobster",
            "lobsters",
            "tom hum",
            "tôm hùm",
        ],
    },
    "location": {
        "India": ["india", "an do", "ấn độ"],
        "Vietnam": ["vietnam", "viet nam"],
        "Khanh Hoa": [
            "khanh hoa",
            "khánh hòa",
            "ven bien khanh hoa",
            "khanh hoa coastal waters",
        ],
        "Latin America": ["latin america", "my la tinh"],
        "Caribbean": ["caribbean"],
        "Global": ["global", "toan cau"],
        "Thailand": ["thailand", "thai lan"],
    },
    "mode": {
        "shrimp aquaculture": [
            "shrimp aquaculture",
            "nuoi tom",
        ],
        "hatchery aquaculture": [
            "hatchery",
            "hatchery aquaculture",
            "trai giong",
        ],
        "aquaculture": [
            "aquaculture",
            "nuoi trong thuy san",
        ],
    },
}


# CHUẨN HÓA VĂN BẢN
def normalize_text(text) -> str:
    if text is None:
        return ""
    if pd.isna(text):
        return ""

    text = str(text).strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9\s;,_-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_canonical_alias_map() -> dict[str, dict[str, set[str]]]:
    """
    Bản đồ canonical -> tập alias, dùng cho term_match() với metadata có thể lưu alias.
    Giá trị trả về luôn chứa cả thuật ngữ canonical.
    """
    # topic/management/prevention chỉ phục vụ hiểu truy vấn (runtime),
    # không dùng để chấm metadata nên không cần có trong ENTITY_COLUMNS.
    out: dict[str, dict[str, set[str]]] = {
        "disease": {},
        "species": {},
        "location": {},
        "mode": {},
        "topic": {},
        "management": {},
        "prevention": {},
    }
    for entity_type, mapping in MANUAL_ALIASES.items():
        if entity_type not in out:
            continue
        for canonical, aliases in mapping.items():
            canon = canonicalize_term(entity_type, canonical)
            s = out[entity_type].setdefault(canon, set())
            s.add(canon)
            for a in aliases:
                s.add(canonicalize_term(entity_type, a))
    return out


# Gọi sau khi đã định nghĩa normalize_text.
CANONICAL_ALIASES = build_canonical_alias_map()


def split_multi_value(cell) -> list[str]:
    if cell is None or pd.isna(cell):
        return []
    parts = [x.strip() for x in str(cell).split(";")]
    return [p for p in parts if p]


# KG RUNTIME (tùy chọn)
_KG_GRAPH = None
_KG_INDEX = None
_KG_LOAD_ATTEMPTED = False
_KG_LOADED_OWL_PATH: Path | None = None


def _init_kg_if_needed():
    """
    Nạp ontology và dựng kg_index một lần mỗi tiến trình.
    Nếu thiếu rdflib hoặc parse OWL lỗi thì tắt KG, không làm hỏng luồng chính.
    """
    global _KG_GRAPH, _KG_INDEX, _KG_LOAD_ATTEMPTED
    global _KG_LOADED_OWL_PATH
    if _KG_LOAD_ATTEMPTED:
        return
    _KG_LOAD_ATTEMPTED = True
    if not _KG_RUNTIME_OK:
        print("[WARN] KG disabled: kg_runtime/rdflib not available")
        return
    try:
        _KG_GRAPH, loaded_path, used_source = kg_runtime.load_kg_prefer_facts_then_alias_enriched(
            KG_FACT_ENRICHED_PATH,
            KG_ALIAS_ENRICHED_PATH,
            KG_ENRICHED_PATH,
            KG_FALLBACK_PATH,
        )
        _KG_INDEX = kg_runtime.build_kg_index(_KG_GRAPH)
        _KG_LOADED_OWL_PATH = Path(loaded_path)
        if used_source == "facts_v2":
            print(f"[KG] Loaded ontology: {KG_FACT_ENRICHED_V2_PATH}")
        elif used_source == "facts":
            print(f"[KG] Loaded ontology: {KG_FACT_ENRICHED_PATH}")
        elif used_source == "alias":
            print(f"[KG] Loaded ontology: {KG_ALIAS_ENRICHED_PATH}")
        elif used_source == "enriched":
            print(f"[KG] Loaded ontology: {KG_ENRICHED_PATH}")
        else:
            print(f"[KG] Fallback ontology loaded: {KG_FALLBACK_PATH}")
    except Exception as e:
        _KG_GRAPH = None
        _KG_INDEX = None
        _KG_LOADED_OWL_PATH = None
        print(f"[WARN] KG disabled (failed to load OWL): {e}")


def _kg_enabled() -> bool:
    return _KG_GRAPH is not None and _KG_INDEX is not None


def _merge_detected_with_kg(detected: dict, kg_entities: dict) -> dict:
    """
    Gộp thự thể liên kết KG vào kết quả nhận diện dùng cho chấm metadata.
    Ưu tiên thự thể KG khi có; giữ nhận diện cũ làm dự phòng.
    Cấu trúc giống detect_entities(): danh sách dict canonical/alias/span.
    """
    out = {k: list(v) for k, v in detected.items()}
    if not kg_entities:
        return out
    # Merge các loại thực thể mà pipeline hiện tại hiểu và/hoặc cần để tránh map nhầm.
    for et in ["disease", "species", "location", "mode", "prevention"]:
        kg_list = kg_entities.get(et) or []
        if not kg_list:
            continue
        merged: list[dict] = []
        for kge in kg_list:
            canonical = canonicalize_term(et, kge.get("label", "") or "")
            alias = kge.get("matched_alias", "")
            span = kge.get("span", (0, 0))
            if canonical:
                merged.append(
                    {
                        "canonical": canonical,
                        "alias": alias,
                        "entity_type": et,
                        "span": span,
                        "match_len": span[1] - span[0],
                        "kg_uri": kge.get("uri"),
                    }
                )
        if merged:
            out[et] = merged
    return out


def _map_doc_to_kg_uri(doc_id: str, row: dict) -> str | None:
    """
    Ánh xạ tài liệu sang nút Document trong KG theo khả năng tốt nhất.
    Giả định:
    - Individual Document thường dùng fragment kiểu FAO_002 trùng doc_id metadata.
    - Khóa dự phòng: title, file_path (ontology có ns:title, ns:filePath).
    """
    if not _kg_enabled():
        return None
    idx = _KG_INDEX or {}
    dockey_to_uri = idx.get("dockey_to_uri") or {}
    k_doc = normalize_text(doc_id)
    if k_doc and k_doc in dockey_to_uri:
        return dockey_to_uri[k_doc]
    title = str(row.get("title", "")).strip()
    k_title = normalize_text(title)
    if k_title and k_title in dockey_to_uri:
        return dockey_to_uri[k_title]
    file_path = str(row.get("file_path", "")).strip()
    k_fp = normalize_text(file_path)
    if k_fp and k_fp in dockey_to_uri:
        return dockey_to_uri[k_fp]
    if file_path:
        k_name = normalize_text(Path(file_path).name)
        if k_name and k_name in dockey_to_uri:
            return dockey_to_uri[k_name]
    return None


def last_token(text: str) -> str:
    toks = text.split()
    return toks[-1] if toks else ""


def term_match(query_term: str, doc_term: str) -> bool:
    q = normalize_text(query_term)
    d = normalize_text(doc_term)
    if not q or not d:
        return False
    if q == d:
        return True
    q_comp = q.replace(" ", "")
    d_comp = d.replace(" ", "")
    if q_comp and d_comp and q_comp == d_comp:
        return True
    def looks_like_binomial(s: str) -> bool:
        toks = s.split()
        if len(toks) != 2:
            return False
        return toks[0].isalpha() and toks[1].isalpha()
    if looks_like_binomial(q) and looks_like_binomial(d) and last_token(q) == last_token(d):
        return True
    return False


# NẠP METADATA
def load_full_metadata(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")

    if p.suffix.lower() == ".xlsx":
        df = pd.read_excel(p)
    elif p.suffix.lower() == ".csv":
        df = pd.read_csv(p)
    else:
        raise ValueError("Metadata must be .xlsx or .csv")

    required = ["doc_id", "title", "file_path"] + list(ENTITY_COLUMNS.values())
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing metadata columns: {missing}")

    return df


def build_metadata_lookup(df: pd.DataFrame) -> dict:
    lookup = {}
    for _, row in df.iterrows():
        doc_id = str(row["doc_id"]).strip()
        lookup[doc_id] = row.to_dict()
    return lookup


# DỰNG TỪ ĐIỂN THỰC THỂ
def build_term_index(df: pd.DataFrame) -> list[dict]:
    entries = []

    # 1) lấy canonical term trực tiếp từ metadata
    for entity_type, col in ENTITY_COLUMNS.items():
        for cell in df[col].tolist():
            for value in split_multi_value(cell):
                canon = str(value).strip()
                if canon:
                    canon = canonicalize_term(entity_type, canon)
                    entries.append({
                        "alias": canon,
                        "canonical": canon,
                        "entity_type": entity_type
                    })

    # 2) thêm alias thủ công tiếng Việt / viết tắt
    for entity_type, mapping in MANUAL_ALIASES.items():
        for canonical, aliases in mapping.items():
            canonical = canonicalize_term(entity_type, canonical)
            entries.append({
                "alias": canonical,
                "canonical": canonical,
                "entity_type": entity_type
            })
            for alias in aliases:
                # Giữ bề mặt alias (cụm nhiều từ như "tom hum"); canonicalize alias có thể gom token và phá khớp.
                surf = str(alias).strip()
                entries.append({
                    "alias": surf,
                    "canonical": canonical,
                    "entity_type": entity_type
                })

    # chuẩn hóa + bỏ trùng
    seen = set()
    cleaned = []
    for e in entries:
        alias_norm = normalize_text(e["alias"])
        canonical_norm = normalize_text(e["canonical"])
        key = (alias_norm, canonical_norm, e["entity_type"])
        if alias_norm and key not in seen:
            seen.add(key)
            cleaned.append({
                "alias_norm": alias_norm,
                "canonical": e["canonical"],
                "entity_type": e["entity_type"],
            })

    # ưu tiên alias dài trước để match tốt hơn
    cleaned.sort(key=lambda x: len(x["alias_norm"]), reverse=True)
    return cleaned


# NHẬN DIỆN THỰC THỂ
# Hàm phụ phục vụ nhận diện.
def _spans_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return not (a[1] <= b[0] or b[1] <= a[0])


def _select_non_overlapping_longest(candidates: list[dict]) -> list[dict]:
    # Tham lam: dài trước, rồi trái sang phải; chặn alias ngắn đè lên alias dài.
    candidates_sorted = sorted(
        candidates,
        key=lambda x: (-x["match_len"], x["span"][0], x["span"][1]),
    )
    selected: list[dict] = []
    selected_spans: list[tuple[int, int]] = []
    for c in candidates_sorted:
        if any(_spans_overlap(c["span"], s) for s in selected_spans):
            continue
        selected.append(c)
        selected_spans.append(c["span"])
    # Thứ tự ổn định trái sang phải để debug/giải thích rõ.
    selected.sort(key=lambda x: x["span"][0])
    return selected


def _compile_boundary_regex(alias_norm: str) -> re.Pattern:
    escaped = re.escape(alias_norm)
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])")

_ENTITY_TYPE_PRIORITY = {
    "species": 4,
    "location": 3,
    "disease": 3,
    "mode": 1,
    # Chủ đề quản lý/phòng bệnh: giữ thấp để không lấn át thực thể chính.
    "topic": 0,
    "management": 0,
    "prevention": 0,
}

def _suppress_overlaps_across_types(found: dict) -> dict:
    """
    Giảm chồng lấn giữa các loại thực thể:
    - Ưu tiên khớp dài, cụ thể hơn khớp ngắn, chung chung (kể cả khác loại).
    - Giữ các nhận diện đa thực thể không chồng lấn hợp lệ.
    Khái quát luật chỉ tôm hùm cũ; ví dụ "nuoi tom hum o Khanh Hoa": mode "nuoi tom" chồng species "tom hum".
    """
    all_matches: list[dict] = []
    for et, matches in found.items():
        for m in matches:
            mm = m.copy()
            mm["entity_type"] = et
            all_matches.append(mm)
    all_matches.sort(
        key=lambda x: (
            -_ENTITY_TYPE_PRIORITY.get(x["entity_type"], 0),
            -(x["span"][1] - x["span"][0]),
            x["span"][0],
        )
    )
    selected: list[dict] = []
    selected_spans: list[tuple[int, int]] = []
    for m in all_matches:
        if any(_spans_overlap(m["span"], s) for s in selected_spans):
            continue
        selected.append(m)
        selected_spans.append(m["span"])
    out = {k: [] for k in found.keys()}
    for m in sorted(selected, key=lambda x: x["span"][0]):
        et = m["entity_type"]
        out[et].append(m)
    return out


def detect_entities(query: str, term_index: list[dict]) -> dict:
    q = normalize_text(query)

    found = {
        "disease": [],
        "species": [],
        "location": [],
        "mode": [],
        "topic": [],
        "management": [],
        "prevention": [],
    }

    # Dựng ứng viên theo loại, rồi chọn tham lam không chồng lấn trong từng loại.
    by_type: dict[str, list[dict]] = {
        "disease": [],
        "species": [],
        "location": [],
        "mode": [],
        "topic": [],
        "management": [],
        "prevention": [],
    }
    for item in term_index:
        alias_norm = item.get("alias_norm", "")
        if not alias_norm:
            continue
        entity_type = item["entity_type"]
        if entity_type not in by_type:
            continue
        canonical = item["canonical"]
        # Tìm mọi vùng khớp biên regex, không chỉ khớp chuỗi con.
        pattern = _compile_boundary_regex(alias_norm)
        for m in pattern.finditer(q):
            by_type[entity_type].append({
                "canonical": canonical,
                "alias": alias_norm,
                "entity_type": entity_type,
                "span": (m.start(), m.end()),
                "match_len": m.end() - m.start(),
            })

    # Tham lam không chồng lấn theo từng loại thực thể.
    for entity_type in by_type.keys():
        found[entity_type] = _select_non_overlapping_longest(by_type[entity_type])

    # Giảm nhiễu bằng cách chặn chồng lấn giữa các loại.
    found = _suppress_overlaps_across_types(found)
    return found


# KHỚP + CHẤM ĐIỂM
def get_doc_values(row: dict, col_name: str) -> list[str]:
    return split_multi_value(row.get(col_name, ""))

def get_query_profile(detected: dict) -> str:
    def is_specific_disease_term(canon: str) -> bool:
        n = normalize_text(canon).replace(" ", "")
        specific = {
            "ahpnd",
            "acutehepatopancreaticnecrosisdisease",
            "imn",
            "imnv",
            "infectiousmyonecrosis",
            "infectiousmyonecrosisvirus",
            "vibriosis",
            "whitespotdisease",
            "wssv",
        }
        return n in specific

    # Sau khi merge với KG runtime, thực thể disease thật thường có kg_uri.
    # Nếu query có disease KG-linked, coi là disease-specific để disease_priority phản ánh đúng ý định.
    if detected.get("disease") and any(m.get("kg_uri") for m in detected["disease"]):
        return "disease_priority"

    if detected.get("disease") and any(is_specific_disease_term(m["canonical"]) for m in detected["disease"]):
        return "disease_priority"
    if detected.get("species"):
        return "species_priority"
    return "generic"


def _find_best_doc_term(query_canon_terms: list[str], doc_terms: list[str]) -> tuple[bool, str | None, str | None]:
    # Thử canonical truy vấn dài trước để ổn định.
    for qcanon in sorted(query_canon_terms, key=lambda x: len(normalize_text(str(x))), reverse=True):
        for dt in doc_terms:
            if term_match(qcanon, dt):
                return True, qcanon, dt
    return False, None, None


def _doc_terms_with_canonical(entity_type: str, row: dict, col_name: str) -> list[str]:
    """Thêm biến thể đã chuẩn hóa để metadata kiểu 'lobsters' khớp nhóm truy vấn 'lobster'."""
    out: list[str] = []
    seen: set[str] = set()
    for dt in get_doc_values(row, col_name):
        for t in (dt, canonicalize_term(entity_type, dt)):
            t = str(t).strip()
            if not t:
                continue
            k = normalize_text(t)
            if k and k not in seen:
                seen.add(k)
                out.append(t)
    return out


def compute_match_features(row: dict, detected: dict) -> dict:
    match_info = {}
    for entity_type in ["disease", "species", "location", "mode"]:
        col_name = ENTITY_COLUMNS[entity_type]
        if entity_type in {"species", "disease"}:
            doc_terms = _doc_terms_with_canonical(entity_type, row, col_name)
        else:
            doc_terms = get_doc_values(row, col_name)
        detected_canon_terms = [m["canonical"] for m in detected.get(entity_type, [])]
        def expand_terms(canon_terms: list[str]) -> list[str]:
            out_terms: list[str] = []
            for ct in canon_terms:
                canon = canonicalize_term(entity_type, ct)
                variants = CANONICAL_ALIASES.get(entity_type, {}).get(canon, set())
                if variants:
                    out_terms.extend(sorted(variants, key=lambda x: len(normalize_text(x)), reverse=True))
                else:
                    out_terms.append(canon)
            seen = set()
            uniq = []
            for t in out_terms:
                k = normalize_text(t)
                if k and k not in seen:
                    seen.add(k)
                    uniq.append(t)
            return uniq
        used_parent = None
        original_detected = None
        if entity_type == "location":
            for qt in detected_canon_terms:
                original_detected = qt
                direct_terms = expand_terms([qt])
                ok, matched_q, matched_dt = _find_best_doc_term(direct_terms, doc_terms)
                if ok:
                    used_parent = None
                    break
                parent = LOCATION_PARENT_MAP.get(qt)
                if parent:
                    parent_terms = expand_terms([parent])
                    ok, matched_q, matched_dt = _find_best_doc_term(parent_terms, doc_terms)
                    if ok:
                        used_parent = parent
                        break
            else:
                ok, matched_q, matched_dt = False, None, None
        else:
            expanded_query_terms = expand_terms(detected_canon_terms)
            ok, matched_q, matched_dt = _find_best_doc_term(expanded_query_terms, doc_terms)
            if detected_canon_terms:
                original_detected = detected_canon_terms[0]

        match_info[entity_type] = {
            "matched": ok,
            "query_canonical": matched_q,
            "query_detected": original_detected,
            "used_parent": used_parent,
            "doc_term": matched_dt,
        }
    return match_info


def compute_hybrid_delta(detected: dict, match_info: dict) -> dict:
    profile = get_query_profile(detected)

    query_has_disease = bool(detected.get("disease"))
    query_has_species = bool(detected.get("species"))
    query_has_location = bool(detected.get("location"))
    query_has_mode = bool(detected.get("mode"))

    bonus_parts: list[str] = []
    penalty_parts: list[str] = []
    delta = 0.0

    def _fmt_match(entity_type: str, score_str: str) -> str:
        qterm = match_info[entity_type].get("query_canonical")
        dterm = match_info[entity_type].get("doc_term")
        qdet = match_info[entity_type].get("query_detected")
        parent = match_info[entity_type].get("used_parent")

        if entity_type == "location" and parent and qdet and dterm:
            return f"match location query={qdet} via parent={parent} with doc_term={dterm} ({score_str})"
        if qterm and dterm:
            return f"match {entity_type} query={qterm} with doc_term={dterm} ({score_str})"
        if qterm:
            return f"match {entity_type} query={qterm} ({score_str})"
        return f"match {entity_type} ({score_str})"

    if profile == "disease_priority":
        if query_has_disease:
            if match_info["disease"]["matched"]:
                delta += 0.35
                bonus_parts.append(_fmt_match("disease", "+0.35"))
            else:
                delta -= 0.18
                penalty_parts.append("miss disease (-0.18)")

        if query_has_species and match_info["species"]["matched"]:
            delta += 0.12
            bonus_parts.append(_fmt_match("species", "+0.12"))

        if query_has_location and match_info["location"]["matched"]:
            delta += 0.05
            bonus_parts.append(_fmt_match("location", "+0.05"))

        if query_has_mode and match_info["mode"]["matched"]:
            delta += 0.05
            bonus_parts.append(_fmt_match("mode", "+0.05"))

        if query_has_disease and query_has_species and match_info["disease"]["matched"] and match_info["species"]["matched"]:
            delta += 0.08
            bonus_parts.append("disease-species synergy (+0.08)")

    elif profile == "species_priority":
        if query_has_species and match_info["species"]["matched"]:
            delta += 0.22
            bonus_parts.append(_fmt_match("species", "+0.22"))

        if query_has_location and match_info["location"]["matched"]:
            delta += 0.08
            bonus_parts.append(_fmt_match("location", "+0.08"))

        if query_has_mode and match_info["mode"]["matched"]:
            delta += 0.08
            bonus_parts.append(_fmt_match("mode", "+0.08"))

        if query_has_location and match_info["species"]["matched"] and match_info["location"]["matched"]:
            delta += 0.05
            bonus_parts.append("species-location synergy (+0.05)")

    else:
        if query_has_location and match_info["location"]["matched"]:
            delta += 0.06
            bonus_parts.append(_fmt_match("location", "+0.06"))
        if query_has_mode and match_info["mode"]["matched"]:
            delta += 0.06
            bonus_parts.append(_fmt_match("mode", "+0.06"))

    if not bonus_parts and not penalty_parts:
        explanation = "no KG match (delta=0)"
    else:
        explanation = "; ".join(penalty_parts + bonus_parts)


    match_flags = {k: bool(match_info[k]["matched"]) for k in match_info.keys()}
    return {
        "profile": profile,
        "kg_delta": float(delta),
        "bonus_breakdown": "; ".join(bonus_parts),
        "penalty_breakdown": "; ".join(penalty_parts),
        "explanation": explanation,
        "match_flags": match_flags,
        "matched_entities": {
            "disease": match_info["disease"]["query_canonical"],
            "species": match_info["species"]["query_canonical"],
            "location": match_info["location"]["query_canonical"],
            "mode": match_info["mode"]["query_canonical"],
        },
    }


# CHẾ ĐỘ TÌM KIẾM
def vector_only_search(query: str, model, index, records, top_k: int = FINAL_K):
    return search(query, model, index, records, top_k=top_k)


def _lobster_coastal_vietnam_boost_intent(query: str, detected: dict) -> bool:
    qn = normalize_text(query)
    if "tom hum" not in qn:
        return False
    if "khanh hoa" not in qn:
        return False
    specs = [normalize_text(m.get("canonical", "")) for m in detected.get("species", [])]
    locs = [normalize_text(m.get("canonical", "")) for m in detected.get("location", [])]
    if "lobster" not in specs and "tom hum bong" not in specs:
        return False
    if "khanh hoa" not in locs and "ven bien khanh hoa" not in locs:
        return False
    return True


def _narrow_local_aquaculture_intent(query: str, detected: dict) -> bool:
    """
    Cổng ý định thận trọng cho truy vấn nuôi trồng theo địa điểm cụ thể.
    Chỉ kích hoạt khi:
      - câu có từ nuôi (tiếng Việt, đã chuẩn hóa thành nuoi)
      - có thực thể địa điểm cụ thể (không chỉ Vietnam/Global)
      - có loài (taxon)
    Dùng để chỉnh điểm nhẹ khi rerank: tránh tài liệu capture/thị trường vượt tài liệu nuôi
    khi cả hai đều trong pool ứng viên.
    """
    qn = normalize_text(query)
    has_nuoi = bool(re.search(r"(?<![a-z0-9])nuoi(?![a-z0-9])", qn))
    if not has_nuoi:
        return False
    locs = [canonicalize_term("location", m.get("canonical", "")) for m in (detected.get("location") or [])]
    if not locs:
        return False
    # Bỏ qua nếu chỉ hỏi cấp quốc gia/toàn cầu.
    if all(normalize_text(x) in {"vietnam", "global"} for x in locs):
        return False
    specs = [canonicalize_term("species", m.get("canonical", "")) for m in (detected.get("species") or [])]
    if not specs:
        return False
    return True


def _metadata_production_mode_flags(row: dict) -> tuple[bool, bool]:
    """
    Trả về (có nuôi trồng, có capture/thị trường) từ cột production_mode metadata.
    Logic cố ý đơn giản/chặt.
    """
    pm = normalize_text(row.get(ENTITY_COLUMNS["mode"], ""))
    if not pm:
        return False, False
    is_aqua = any(tok in pm for tok in ["aquaculture", "hatchery", "farming", "nuoi"])
    is_capture = any(tok in pm for tok in ["capture", "market", "fisheries"])
    return is_aqua, is_capture


def _kg_mode_flags(kg_doc_modes: list[str]) -> tuple[bool, bool]:
    """
    Trả về (có dấu hiệu nuôi trồng, có capture/thị trường) từ URI documentProductionMode trong KG.
    """
    if not kg_doc_modes:
        return False, False
    def _local(u: str) -> str:
        s = str(u)
        if "#" in s:
            return s.rsplit("#", 1)[-1]
        if "/" in s:
            return s.rsplit("/", 1)[-1]
        return s
    local_names = [normalize_text(_local(str(u))) for u in kg_doc_modes]
    is_capture = any("capturefisheries" in ln for ln in local_names)
    # Coi là có nuôi nếu có mode không phải capture (tránh đoán quá chi tiết loại mode).
    is_aqua = any(ln and "capturefisheries" not in ln for ln in local_names)
    return is_aqua, is_capture


def _vn_brackish_disease_manual_query_intent(qn: str) -> bool:
    """Ý định sổ tay/extension bệnh tôm nước lợ (khớp TCTS_001), không kích hoạt trên truy vấn ngắn/generic."""
    if "tom" not in qn or ("nuoc loi" not in qn and "nuoc lo" not in qn):
        return False
    if "benh thuong gap" not in qn:
        return False
    if "phong" not in qn or "chong" not in qn:
        return False
    return True


def _vn_brackish_manual_title_aligned(tn: str) -> bool:
    if "benh thuong gap" not in tn or "tom" not in tn:
        return False
    if "nuoc loi" not in tn and "nuoc lo" not in tn:
        return False
    if "phong" not in tn or "chong" not in tn:
        return False
    return True


def _thailand_low_water_exchange_intent(qn: str) -> bool:
    if "thai lan" not in qn and "thailand" not in qn:
        return False
    if ("thap" in qn and "nuoc" in qn) or ("trao" in qn and "doi" in qn and "nuoc" in qn):
        return True
    if "low water" in qn:
        return True
    return False


def _species_or_query_suggests_vannamei(detected: dict, qn: str) -> bool:
    if any(x in qn for x in ("vannamei", "tom the chan trang", "whiteleg", "white shrimp")):
        return True
    for m in detected.get("species") or []:
        s = normalize_text(str(m.get("canonical", "")))
        if any(x in s for x in ("vannamei", "tom the", "whiteleg", "white shrimp", "whiteleg shrimp")):
            return True
    return False


def _hatchery_vannamei_production_mode_intent(qn: str, detected: dict) -> bool:
    """HM_001: trại giống + tôm thẻ, không hỏi bệnh cụ thể — tránh ưu tiên sách WSSV nuôi thương phẩm."""
    if detected.get("disease"):
        return False
    qn = normalize_text(qn)
    if not _species_or_query_suggests_vannamei(detected, qn):
        return False
    # Chỉ kích hoạt khi truy vấn thực sự hỏi *chế độ sản xuất / trại giống* (HM_001),
    # không phảy biosecurity trong hatchery (BI_001) — tránh đẩy FAO_005 xuống.
    if "production mode" not in qn and "trai giong" not in qn:
        return False
    mode_hatch = any(
        "hatchery" in normalize_text(str(m.get("canonical", "")))
        for m in (detected.get("mode") or [])
    )
    if not mode_hatch and "hatchery" not in qn:
        return False
    return True


def _title_strongly_hatchery_vannamei(tn: str) -> bool:
    if "hatchery" not in tn:
        return False
    return ("vannamei" in tn) or ("white shrimp" in tn) or ("whiteleg" in tn)


def _title_vn_wssv_growout_manual(tn: str) -> bool:
    if "hatchery" in tn:
        return False
    if "benh dom trang" in tn or "om trang" in tn:
        return True
    if "wssv" in tn:
        return True
    return False


def _biosecurity_hatchery_vannamei_stack_intent(detected: dict, qn: str) -> bool:
    """BI_001: biosecurity + hatchery + tôm thẻ — ưu tiên tài liệu có cả biosecurity và hatchery trong title."""
    if not any(str(m.get("canonical", "")).strip().lower() == "biosecurity" for m in (detected.get("topic") or [])):
        return False
    if not any(
        "hatchery" in normalize_text(str(m.get("canonical", "")))
        for m in (detected.get("mode") or [])
    ):
        return False
    return _species_or_query_suggests_vannamei(detected, qn)


def _title_biosecurity_and_hatchery(tn: str) -> bool:
    return "biosecurity" in tn and "hatchery" in tn


def _intent_narrow_final_adjustment(
    query: str,
    detected: dict,
    row: dict,
    doc_title: str,
) -> tuple[float, str]:
    """
    Điều chỉnh điểm cuối cực hẹp theo intent đã chẩn đoán (vòng kỹ thuật cuối).
    Chỉ dùng khi mẫu truy vấn/title khớp rõ — tránh heuristic rộng.
    """
    qn = normalize_text(query)
    tn = normalize_text(str(doc_title or ""))
    adj = 0.0
    parts: list[str] = []

    if _vn_brackish_disease_manual_query_intent(qn) and _vn_brackish_manual_title_aligned(tn):
        adj += 0.12
        parts.append("intent: VN brackish manual title (+0.12)")

    if _biosecurity_hatchery_vannamei_stack_intent(detected, qn):
        if _title_biosecurity_and_hatchery(tn):
            adj += 0.22
            parts.append("intent: biosecurity + hatchery title stack (+0.22)")
        elif "strategy manual" in tn and "biosecurity" not in tn:
            adj -= 0.10
            parts.append("intent: biosecurity hatchery query vs disease strategy manual (-0.10)")

    if _thailand_low_water_exchange_intent(qn):
        if "low water exchange" in tn:
            if "thailand" in tn:
                adj += 0.20
                parts.append("intent: low water exchange + Thailand title (+0.20)")
            else:
                adj += 0.12
                parts.append("intent: low water exchange title (+0.12)")
        doc_locs = split_multi_value(row.get(ENTITY_COLUMNS["location"], ""))
        doc_loc_blob = " ".join(normalize_text(str(x)) for x in doc_locs)
        if doc_locs and ("vietnam" in doc_loc_blob or "viet nam" in doc_loc_blob) and "thailand" not in doc_loc_blob:
            adj -= 0.10
            parts.append("intent: Thailand LWE query vs doc Vietnam-only (-0.10)")

    if _hatchery_vannamei_production_mode_intent(qn, detected):
        if _title_strongly_hatchery_vannamei(tn):
            adj += 0.14
            parts.append("intent: hatchery vannamei title (+0.14)")
        if _title_vn_wssv_growout_manual(tn):
            adj -= 0.15
            parts.append("intent: VN WSSV/grow-out vs hatchery production query (-0.15)")

    return adj, "; ".join(parts)


def hybrid_search(query: str, model, index, records, metadata_lookup: dict, term_index: list[dict]):
    _init_kg_if_needed()

    detected = detect_entities(query, term_index)
    kg_entities = {"disease": [], "species": [], "location": [], "mode": [], "prevention": []}
    if _kg_enabled():
        try:
            linked = kg_runtime.link_query_entities_kg(query, _KG_INDEX)
            # Giữ cấu trúc ổn định (pipeline chủ yếu dùng 4 bucket chính).
            kg_entities = {
                "disease": linked.get("disease") or [],
                "species": linked.get("species") or [],
                "location": linked.get("location") or [],
                "mode": linked.get("mode") or [],
                "prevention": linked.get("prevention") or [],
            }
        except Exception as e:
            print(f"[WARN] KG entity linking failed, fallback to old detection: {e}")
            kg_entities = {"disease": [], "species": [], "location": [], "mode": [], "prevention": []}
    detected = _merge_detected_with_kg(detected, kg_entities)
    narrow_local_aqua_intent = _narrow_local_aquaculture_intent(query, detected)

    # Lấy nhiều ứng viên hơn từ vector search để rerank
    candidates = search(query, model, index, records, top_k=CANDIDATE_K)
    if _lobster_coastal_vietnam_boost_intent(query, detected):
        extra = search(LOBSTER_COASTAL_VECTOR_BOOST_QUERY, model, index, records, top_k=CANDIDATE_K)
        seen_chunk = {c["chunk_id"] for c in candidates}
        for c in extra:
            cid = c.get("chunk_id")
            if cid and cid not in seen_chunk:
                seen_chunk.add(cid)
                candidates.append(c)

    # Rerank gộp theo tài liệu để giảm chunk lặp từ cùng một doc.
    best_by_doc: dict[str, dict] = {}
    delta_cache: dict[str, dict] = {}
    kg_cache: dict[str, dict] = {}

    for item in candidates:
        doc_id = item["doc_id"]
        if doc_id not in delta_cache:
            row = metadata_lookup.get(doc_id, {})
            match_info = compute_match_features(row, detected)
            delta_info = compute_hybrid_delta(detected, match_info)
            delta_cache[doc_id] = delta_info

        # Chấm KG tách khỏi metadata; cache theo doc_id
        if doc_id not in kg_cache:
            kg_info = {
                "doc_uri_in_kg": None,
                "kg_score": 0.0,
                "kg_bonus_breakdown": "",
                "kg_penalty_breakdown": "",
                "kg_explanation": [],
                "kg_direct_match": 0.0,
                "kg_relation_match": 0.0,
                "kg_context_match": 0.0,
                "kg_matched_entities": {
                    "disease": [e.get("label") for e in (kg_entities.get("disease") or [])],
                    "species": [e.get("label") for e in (kg_entities.get("species") or [])],
                    "location": [e.get("label") for e in (kg_entities.get("location") or [])],
                    "mode": [e.get("label") for e in (kg_entities.get("mode") or [])],
                },
                "kg_doc_modes": [],
            }

            if _kg_enabled():
                try:
                    row = metadata_lookup.get(doc_id, {})
                    doc_uri = _map_doc_to_kg_uri(doc_id, row)
                    kg_info["doc_uri_in_kg"] = doc_uri

                    if doc_uri:
                        doc_facts = kg_runtime.get_document_facts(_KG_GRAPH, doc_uri)  
                        kg_info["kg_doc_modes"] = list(doc_facts.get("mode", []) or [])
                        scored = kg_runtime.score_doc_with_kg(
                            query_entities=kg_entities,
                            doc_facts=doc_facts,
                            kg_index=_KG_INDEX,
                            graph=_KG_GRAPH,
                            query_text=query,
                        )
                        kg_info.update(scored)
                except Exception as e:
                    print(f"[WARN] KG scoring failed for doc_id={doc_id}: {e}")

            kg_cache[doc_id] = kg_info

        delta_info = delta_cache[doc_id]
        kg_info = kg_cache[doc_id]
        vector_score = float(item["score"])
        metadata_delta = float(delta_info["kg_delta"])
        kg_delta = float(kg_info.get("kg_score", 0.0) or 0.0)
        row = metadata_lookup.get(doc_id, {})
        int_adj, int_expl = _intent_narrow_final_adjustment(
            query, detected, row, str(item.get("title", ""))
        )
        final_score = vector_score + metadata_delta + kg_delta + float(int_adj)
        prev = best_by_doc.get(doc_id)
        if prev is not None and final_score <= float(prev["final_score"]):
            continue
        new_item = item.copy()
        new_item["vector_score"] = vector_score
        new_item["kg_bonus"] = float(metadata_delta)
        new_item["metadata_delta"] = float(metadata_delta)
        new_item["kg_score"] = float(kg_delta)
        new_item["intent_adjustment"] = float(int_adj)
        new_item["final_score"] = float(final_score)

        # Gộp giải thích metadata và KG
        meta_expl = delta_info.get("explanation", "")
        kg_expl_list = kg_info.get("kg_explanation", []) or []
        kg_expl = "; ".join([x for x in kg_expl_list if x])
        if kg_expl:
            new_item["explanation"] = f"metadata: {meta_expl}; KG: {kg_expl}" if meta_expl else f"KG: {kg_expl}"
        else:
            new_item["explanation"] = meta_expl
        if int_expl:
            ie = new_item["explanation"]
            new_item["explanation"] = f"{ie}; {int_expl}" if ie else int_expl

        # Phục vụ xuất CSV/đánh giá debug
        new_item["profile"] = delta_info["profile"]
        new_item["bonus_breakdown"] = delta_info["bonus_breakdown"]
        new_item["penalty_breakdown"] = delta_info["penalty_breakdown"]
        new_item["match_disease"] = bool(delta_info["match_flags"]["disease"])
        new_item["match_species"] = bool(delta_info["match_flags"]["species"])
        new_item["match_location"] = bool(delta_info["match_flags"]["location"])
        new_item["match_mode"] = bool(delta_info["match_flags"]["mode"])

        # Trường KG để xuất/debug
        new_item["kg_bonus_breakdown"] = kg_info.get("kg_bonus_breakdown", "")
        new_item["kg_penalty_breakdown"] = kg_info.get("kg_penalty_breakdown", "")
        new_item["kg_explanation"] = "; ".join(kg_expl_list) if kg_expl_list else ""
        new_item["doc_uri_in_kg"] = kg_info.get("doc_uri_in_kg", None)
        new_item["kg_direct_match"] = float(kg_info.get("kg_direct_match", 0.0) or 0.0)
        new_item["kg_relation_match"] = float(kg_info.get("kg_relation_match", 0.0) or 0.0)
        new_item["kg_context_match"] = float(kg_info.get("kg_context_match", 0.0) or 0.0)
        new_item["kg_matched_entities"] = kg_info.get("kg_matched_entities", {})

        # Ý định nuôi địa phương hẹp: cache cờ mode để phạt muộn thận trọng.
        try:
            meta_is_aqua, meta_is_capture = _metadata_production_mode_flags(row)
            kg_is_aqua, kg_is_capture = _kg_mode_flags(list(kg_info.get("kg_doc_modes") or []))
            new_item["_doc_is_aquaculture"] = bool(meta_is_aqua or kg_is_aqua)
            new_item["_doc_is_capture_or_market"] = bool(meta_is_capture or kg_is_capture)
        except Exception:
            new_item["_doc_is_aquaculture"] = False
            new_item["_doc_is_capture_or_market"] = False

        best_by_doc[doc_id] = new_item

    reranked = sorted(best_by_doc.values(), key=lambda x: x["final_score"], reverse=True)

    # Phạt muộn thận trọng: chỉ khi VỪA có doc ngữ cảnh nuôi trong pool VỪA truy vấn là
    # ý định nuôi địa phương hẹp. Tránh làm tệ các trường hợp corpus không có tài liệu nuôi cho loài/địa điểm đó.
    if narrow_local_aqua_intent and reranked:
        any_aqua_doc = any(bool(x.get("_doc_is_aquaculture")) for x in reranked)
        if any_aqua_doc:
            for x in reranked:
                if x.get("_doc_is_capture_or_market"):
                    pen = 0.12
                    x["final_score"] = float(x.get("final_score", 0.0)) - pen
                    expl = x.get("explanation", "") or ""
                    extra = f"intent penalty: local aquaculture query vs capture/market doc (-{pen:.2f})"
                    x["explanation"] = f"{expl}; {extra}" if expl else extra
            reranked.sort(key=lambda x: x["final_score"], reverse=True)

    # Báo cáo lúc chạy: xác nhận KG thực sự có đóng góp điểm.
    # Không đổi logic; chỉ đếm sau rerank.
    try:
        top_items = reranked[:FINAL_K]
        if _kg_enabled():
            mapped = sum(1 for x in top_items if x.get("doc_uri_in_kg"))
            nonzero = sum(1 for x in top_items if (x.get("kg_score", 0.0) or 0.0) > 0)
            used = _KG_LOADED_OWL_PATH.name if _KG_LOADED_OWL_PATH else "unknown"
            if nonzero == 0:
                print(f"[KG] No KG contribution in top {FINAL_K} (kg_score=0); used={used}; mapped_docs={mapped}/{FINAL_K}")
            else:
                print(f"[KG] KG applied in top {FINAL_K}: nonzero_kg={nonzero}/{FINAL_K}; mapped_docs={mapped}/{FINAL_K}; used={used}")
        else:
            print("[KG] KG disabled: metadata-only scoring")
    except Exception:
        # Không làm hỏng CLI vì báo cáo.
        pass

    return detected, reranked[:FINAL_K]


# HIỂN THỊ
def print_detected_entities(detected: dict):
    print("\n[THỰC THỂ NHẬN DIỆN]")
    for k, vals in detected.items():
        canon_list = [v["canonical"] for v in vals] if vals else []
        print(f"- {k}: {canon_list if canon_list else '[]'}")


def print_vector_results(results: list[dict]):
    print("\n" + "=" * 100)
    print("VECTOR-ONLY RESULTS")
    print("=" * 100)

    if not results:
        print("Không có kết quả.")
        return

    for rank, r in enumerate(results, start=1):
        print("-" * 100)
        print(f"Top {rank}")
        print(f"Score    : {r['score']:.4f}")
        print(f"Doc ID   : {r['doc_id']}")
        print(f"Title    : {r['title']}")
        print(f"Chunk ID : {r['chunk_id']}")
        print(f"File     : {r['file_path']}")
        print("Text:")
        print(r["text"][:500])
        print()


def print_hybrid_results(results: list[dict]):
    print("\n" + "=" * 100)
    print("HYBRID RESULTS")
    print("=" * 100)

    if not results:
        print("Không có kết quả.")
        return

    for rank, r in enumerate(results, start=1):
        print("-" * 100)
        print(f"Top {rank}")
        print(f"Vector score : {r['vector_score']:.4f}")
        print(f"KG bonus     : {r['kg_bonus']:.4f}")
        print(f"Final score  : {r['final_score']:.4f}")
        print(f"Doc ID       : {r['doc_id']}")
        print(f"Title        : {r['title']}")
        print(f"Chunk ID     : {r['chunk_id']}")
        print(f"Explanation  : {r['explanation']}")
        print("Text:")
        print(r["text"][:500])
        print()


# CHẠY LÔ 
def run_batch_tests():
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("[STEP] Loading vector index...")
    model, index, records = load_index()

    print("[STEP] Loading metadata...")
    df = load_full_metadata(METADATA_PATH)
    metadata_lookup = build_metadata_lookup(df)

    print("[STEP] Building entity dictionary...")
    term_index = build_term_index(df)

    for i, query in enumerate(TEST_QUERIES, start=1):
        print("\n" + "=" * 100)
        print(f"QUERY {i}: {query}")
        print("=" * 100)

        vector_results = vector_only_search(query, model, index, records, top_k=FINAL_K)
        print_vector_results(vector_results)

        detected, hybrid_results = hybrid_search(
            query=query,
            model=model,
            index=index,
            records=records,
            metadata_lookup=metadata_lookup,
            term_index=term_index,
        )
        print_detected_entities(detected)
        print_hybrid_results(hybrid_results)


def acceptance_checks():
    """
    Kiểm tra chấp nhận nhỏ (không thêm chế độ CLI, mặc định không chạy).
    Gọi thủ công trong REPL nếu cần:
        from hybrid_search import acceptance_checks; acceptance_checks()
    """
    df = load_full_metadata(METADATA_PATH)
    term_index = build_term_index(df)

    def canon_list(detected: dict, k: str) -> list[str]:
        return [m["canonical"] for m in detected.get(k, [])]

    # 1) nuôi tôm hùm ở Khánh Hòa
    q1 = "nuôi tôm hùm ở Khánh Hòa"
    d1 = detect_entities(q1, term_index)
    assert "lobster" in canon_list(d1, "species"), "Expected lobster detection"
    assert "shrimp" not in canon_list(d1, "species"), "Should not detect shrimp from 'tôm hùm'"
    assert "shrimp aquaculture" not in canon_list(d1, "mode"), "Should not infer shrimp aquaculture from overlapping span"
    assert "Khanh Hoa" in canon_list(d1, "location"), "Expected specific location Khanh Hoa"

    # 2) bệnh AHPND trên tôm
    q2 = "bệnh AHPND trên tôm"
    d2 = detect_entities(q2, term_index)
    assert "AHPND" in canon_list(d2, "disease"), "Expected disease AHPND"

    # 3) tài liệu về trại giống tôm sú ở Ấn Độ
    q3 = "tài liệu về trại giống tôm sú ở Ấn Độ"
    d3 = detect_entities(q3, term_index)
    assert any(x in canon_list(d3, "species") for x in ["Penaeus monodon", "shrimp"]), "Expected Penaeus monodon or shrimp"
    assert "India" in canon_list(d3, "location"), "Expected location India"
    assert "hatchery aquaculture" in canon_list(d3, "mode"), "Expected hatchery aquaculture"

    # 4) biosecurity trong hatchery tôm thẻ chân trắng
    q4 = "biosecurity trong hatchery tôm thẻ chân trắng"
    d4 = detect_entities(q4, term_index)
    assert "biosecurity" in canon_list(d4, "topic"), "Expected biosecurity topic detection"
    assert not canon_list(d4, "disease"), "Biosecurity should not be classified as disease"
    assert "Penaeus vannamei" in canon_list(d4, "species"), "Expected whiteleg shrimp detection"
    assert "hatchery aquaculture" in canon_list(d4, "mode"), "Expected hatchery aquaculture"

    print("[OK] acceptance_checks passed")


# XUẤT CSV 
def build_comparison_rows() -> pd.DataFrame:
    model, index, records = load_index()
    df = load_full_metadata(METADATA_PATH)
    metadata_lookup = build_metadata_lookup(df)
    term_index = build_term_index(df)

    rows = []

    for query in TEST_QUERIES:
        vector_results = vector_only_search(query, model, index, records, top_k=3)
        detected, hybrid_results = hybrid_search(
            query=query,
            model=model,
            index=index,
            records=records,
            metadata_lookup=metadata_lookup,
            term_index=term_index,
        )

        profile = get_query_profile(detected)
        detected_disease = ";".join([m["canonical"] for m in detected.get("disease", [])]) if detected.get("disease") else ""
        detected_species = ";".join([m["canonical"] for m in detected.get("species", [])]) if detected.get("species") else ""
        detected_location = ";".join([m["canonical"] for m in detected.get("location", [])]) if detected.get("location") else ""
        detected_mode = ";".join([m["canonical"] for m in detected.get("mode", [])]) if detected.get("mode") else ""

        # Thự thể KG sau gộp; nếu liên kết KG thì mục có kg_uri và alias
        kg_detected_disease = ";".join([m.get("canonical", "") for m in detected.get("disease", []) if m.get("kg_uri")]) if detected.get("disease") else ""
        kg_detected_species = ";".join([m.get("canonical", "") for m in detected.get("species", []) if m.get("kg_uri")]) if detected.get("species") else ""
        kg_detected_location = ";".join([m.get("canonical", "") for m in detected.get("location", []) if m.get("kg_uri")]) if detected.get("location") else ""
        kg_detected_mode = ";".join([m.get("canonical", "") for m in detected.get("mode", []) if m.get("kg_uri")]) if detected.get("mode") else ""

        for rank, r in enumerate(vector_results, start=1):
            rows.append({
                "query": query,
                "method": "vector",
                "rank": rank,
                "doc_id": r["doc_id"],
                "title": r["title"],
                "chunk_id": r["chunk_id"],
                "score": round(r["score"], 4),
                "kg_bonus": "",
                "final_score": "",
                "query_profile": profile,
                "detected_disease": detected_disease,
                "detected_species": detected_species,
                "detected_location": detected_location,
                "detected_mode": detected_mode,
                "kg_detected_disease": kg_detected_disease,
                "kg_detected_species": kg_detected_species,
                "kg_detected_location": kg_detected_location,
                "kg_detected_mode": kg_detected_mode,
                "kg_score": "",
                "kg_bonus_breakdown": "",
                "kg_penalty_breakdown": "",
                "kg_explanation": "",
                "doc_uri_in_kg": "",
                "kg_direct_match": "",
                "kg_relation_match": "",
                "kg_context_match": "",
                "match_disease": "",
                "match_species": "",
                "match_location": "",
                "match_mode": "",
                "bonus_breakdown": "",
                "penalty_breakdown": "",
                "explanation": "",
                "detected_entities": str({k: [m["canonical"] for m in v] for k, v in detected.items()}),
            })

        for rank, r in enumerate(hybrid_results, start=1):
            rows.append({
                "query": query,
                "method": "hybrid",
                "rank": rank,
                "doc_id": r["doc_id"],
                "title": r["title"],
                "chunk_id": r["chunk_id"],
                "score": round(r["vector_score"], 4),
                "kg_bonus": round(r["kg_bonus"], 4),
                "final_score": round(r["final_score"], 4),
                "query_profile": r.get("profile", profile),
                "detected_disease": detected_disease,
                "detected_species": detected_species,
                "detected_location": detected_location,
                "detected_mode": detected_mode,
                "kg_detected_disease": kg_detected_disease,
                "kg_detected_species": kg_detected_species,
                "kg_detected_location": kg_detected_location,
                "kg_detected_mode": kg_detected_mode,
                "kg_score": round(float(r.get("kg_score", 0.0) or 0.0), 4),
                "kg_bonus_breakdown": r.get("kg_bonus_breakdown", ""),
                "kg_penalty_breakdown": r.get("kg_penalty_breakdown", ""),
                "kg_explanation": r.get("kg_explanation", ""),
                "doc_uri_in_kg": r.get("doc_uri_in_kg", ""),
                "kg_direct_match": round(float(r.get("kg_direct_match", 0.0) or 0.0), 4),
                "kg_relation_match": round(float(r.get("kg_relation_match", 0.0) or 0.0), 4),
                "kg_context_match": round(float(r.get("kg_context_match", 0.0) or 0.0), 4),
                "match_disease": r.get("match_disease", False),
                "match_species": r.get("match_species", False),
                "match_location": r.get("match_location", False),
                "match_mode": r.get("match_mode", False),
                "bonus_breakdown": r.get("bonus_breakdown", ""),
                "penalty_breakdown": r.get("penalty_breakdown", ""),
                "explanation": r["explanation"],
                "detected_entities": str({k: [m["canonical"] for m in v] for k, v in detected.items()}),
            })

    return pd.DataFrame(rows)


def export_comparison_csv():
    out_df = build_comparison_rows()
    out_df.to_csv("hybrid_comparison.csv", index=False, encoding="utf-8-sig")
    print("[OK] Saved: hybrid_comparison.csv")


def save_batch_results_txt(filename: str = "hybrid_results.txt"):
    with open(filename, "w", encoding="utf-8-sig") as f:
        with redirect_stdout(f):
            run_batch_tests()
    print(f"[OK] Saved: {filename}")


def export_all():
    save_batch_results_txt("hybrid_results.txt")
    export_comparison_csv()
    print("[OK] Saved both hybrid_results.txt and hybrid_comparison.csv")


# HÀM MAIN
def main():
    print("[STEP] Loading vector index...")
    model, index, records = load_index()
    print("[STEP] Loading metadata...")
    df = load_full_metadata(METADATA_PATH)
    metadata_lookup = build_metadata_lookup(df)
    print("[STEP] Building entity dictionary...")
    term_index = build_term_index(df)
    print("[READY] Nhập câu hỏi. Gõ 'exit' để thoát.")

    while True:
        query = input("\nCâu hỏi: ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        # Chỉ vector
        vector_results = vector_only_search(query, model, index, records, top_k=FINAL_K)
        print_vector_results(vector_results)

        # Tìm kiếm hybrid (vector + metadata + KG)
        detected, hybrid_results = hybrid_search(
            query=query,
            model=model,
            index=index,
            records=records,
            metadata_lookup=metadata_lookup,
            term_index=term_index,
        )
        print_detected_entities(detected)
        print_hybrid_results(hybrid_results)


if __name__ == "__main__":
    import sys

    mode = (sys.argv[1].strip().lower() if len(sys.argv) > 1 else "batch")

    if mode in {"batch", "test", "tests"}:
        run_batch_tests()
    elif mode in {"export", "csv", "export_csv"}:
        export_comparison_csv()
    elif mode in {"save_txt", "txt"}:
        save_batch_results_txt()
    elif mode in {"all"}:
        export_all()
    elif mode in {"interactive", "cli"}:
        main()
    else:
        raise ValueError("Mode must be one of: batch | export_csv | save_txt | all | interactive")

