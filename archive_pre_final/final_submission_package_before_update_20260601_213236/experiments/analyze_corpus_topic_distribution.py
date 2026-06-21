from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = PROJECT_ROOT / "data" / "metadata" / "document_metadata_cleaned.xlsx"
OUT_DIR = PROJECT_ROOT / "outputs"
FIG_DIR = OUT_DIR / "figures"

TOPIC_CSV = OUT_DIR / "corpus_topic_distribution.csv"
SOURCE_CSV = OUT_DIR / "corpus_topic_distribution_by_source.csv"
LOCATION_CSV = OUT_DIR / "corpus_topic_distribution_by_location.csv"
DOC_LABELS_CSV = OUT_DIR / "corpus_topic_distribution_document_labels.csv"
REPORT_MD = OUT_DIR / "corpus_topic_distribution_report.md"
FIG_PATH = FIG_DIR / "fig_corpus_topic_distribution.png"


TOPIC_ORDER = [
    "aquatic_disease",
    "marine_aquaculture",
    "hatchery_seed_production",
    "biosecurity_management",
    "environment_water_quality",
    "local_vietnam_khanhhoa",
    "species_taxon_specific",
    "general_policy_technical",
    "uncategorized",
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("đ", "d")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def detect_column(columns: list[str], candidates: list[str]) -> str | None:
    normalized = {normalize_text(c).replace(" ", "_"): c for c in columns}
    for cand in candidates:
        key = normalize_text(cand).replace(" ", "_")
        if key in normalized:
            return normalized[key]
    for cand in candidates:
        cand_norm = normalize_text(cand).replace(" ", "")
        for col in columns:
            col_norm = normalize_text(col).replace(" ", "").replace("_", "")
            if cand_norm == col_norm or cand_norm in col_norm:
                return col
    return None


def contains_any(text: str, keywords: list[str]) -> list[str]:
    hits = []
    padded = f" {text} "
    for kw in keywords:
        k = normalize_text(kw)
        if not k:
            continue
        if re.search(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])", padded):
            hits.append(kw)
    return hits


def split_multi(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    parts = re.split(r";|\||,", text)
    return [p.strip() for p in parts if p and p.strip()]


def source_group(row: dict[str, Any], source_col: str | None, doc_id_col: str | None) -> str:
    raw_source = clean(row.get(source_col, "")) if source_col else ""
    doc_id = clean(row.get(doc_id_col, "")) if doc_id_col else ""
    text = normalize_text(f"{raw_source} {doc_id}")
    if "fao" in text:
        return "FAO"
    if "naca" in text:
        return "NACA"
    if "seafdec" in text:
        return "SEAFDEC"
    if "pmc" in text or "plos" in text or "mdpi" in text or "scientific reports" in text or "frontiers" in text:
        return "PMC/journal"
    if "ria3" in text or "vien nghien cuu nuoi trong thuy san iii" in text:
        return "RIA3"
    if "tcts" in text or "tong cuc thuy san" in text:
        return "TCTS"
    if "tep bac" in text or doc_id.upper().startswith("TB_"):
        return "TB"
    if "tckhts" in text or "tap chi khoa hoc" in text:
        return "Vietnamese journal"
    return raw_source or "Other"


def field_blob(row: dict[str, Any], cols: dict[str, str | None], names: list[str]) -> str:
    values = []
    for name in names:
        col = cols.get(name)
        if col:
            values.append(clean(row.get(col, "")))
    return " ".join(values)


def classify_document(row: dict[str, Any], cols: dict[str, str | None]) -> tuple[list[str], list[str], str]:
    title = field_blob(row, cols, ["title"])
    source = field_blob(row, cols, ["source"])
    doc_type = field_blob(row, cols, ["doc_type"])
    taxon = field_blob(row, cols, ["taxon"])
    disease = field_blob(row, cols, ["disease"])
    pathogen = field_blob(row, cols, ["pathogen"])
    symptom = field_blob(row, cols, ["symptom"])
    prevention = field_blob(row, cols, ["prevention"])
    treatment = field_blob(row, cols, ["treatment"])
    production = field_blob(row, cols, ["production_mode"])
    location = field_blob(row, cols, ["location", "country", "region"])
    summary = field_blob(row, cols, ["summary", "abstract", "notes", "keywords"])
    all_text = normalize_text(" ".join([title, source, doc_type, taxon, disease, pathogen, symptom, prevention, treatment, production, location, summary]))

    labels: list[str] = []
    evidence: list[str] = []

    disease_keywords = [
        "disease", "pathogen", "ahpnd", "ems", "wssv", "ehp", "imnv", "imn",
        "infectious myonecrosis", "white spot", "vibriosis", "vibrio", "diagnosis",
        "diagnostic", "surveillance", "health", "disease control", "mortality",
        "necrosis", "hepatopancreatic", "microsporidiosis", "syndrome",
    ]
    marine_keywords = [
        "marine aquaculture", "mariculture", "cage culture", "lobster", "marine fish",
        "coastal aquaculture", "coastal", "sea farming", "nuoi bien", "long be",
        "cam ranh", "van ninh", "van phong",
    ]
    hatchery_keywords = [
        "hatchery", "seed production", "larval", "larvae", "post larvae",
        "postlarvae", "post larval", "broodstock", "nursery", "zoea", "pl",
        "trai giong", "tom giong",
    ]
    biosecurity_keywords = [
        "biosecurity", "an toan sinh hoc", "prevention", "health management",
        "disease management", "risk", "risk analysis", "risk management",
        "surveillance", "zoning", "control measure", "control measures",
        "phong benh", "kiem soat", "emergency preparedness",
    ]
    environment_keywords = [
        "water quality", "environment", "environmental", "salinity", "temperature",
        "dissolved oxygen", "oxygen", "pollution", "pond", "climate", "monitoring",
        "quan trac", "moi truong", "ph", "carrying capacity", "stress",
    ]
    local_keywords = [
        "vietnam", "viet nam", "khanh hoa", "nha trang", "cam ranh", "van ninh",
        "mekong delta", "dbscl", "dong bang song cuu long", "phu yen",
        "binh dinh", "ninh thuan", "binh thuan", "ha tinh", "thach ha",
        "cam xuyen", "nghi xuan", "ca mau", "nam trung bo",
    ]
    species_keywords = [
        "shrimp", "prawn", "lobster", "fish", "penaeus", "litopenaeus",
        "monodon", "vannamei", "tiger shrimp", "whiteleg shrimp", "white shrimp",
        "grouper", "seabass", "tilapia", "tom", "tom the", "tom su", "tom hum",
        "mud crab", "scylla",
    ]
    general_keywords = [
        "report", "manual", "guide", "guideline", "policy", "technical",
        "overview", "toolkit", "aquaculture", "fisheries", "fishery",
        "sustainable", "governance", "planning", "handbook", "proceedings",
    ]

    if disease or pathogen or symptom or prevention or treatment:
        labels.append("aquatic_disease")
        evidence.append("field: disease/pathogen/symptom/prevention/treatment")
    else:
        hits = contains_any(all_text, disease_keywords)
        if hits:
            labels.append("aquatic_disease")
            evidence.append("keywords: " + ", ".join(hits[:5]))

    marine_hits = contains_any(normalize_text(" ".join([production, location, title, summary])), marine_keywords)
    if marine_hits:
        labels.append("marine_aquaculture")
        evidence.append("marine keywords/fields: " + ", ".join(marine_hits[:5]))

    hatchery_hits = contains_any(normalize_text(" ".join([production, title, summary])), hatchery_keywords)
    if hatchery_hits:
        labels.append("hatchery_seed_production")
        evidence.append("hatchery keywords/fields: " + ", ".join(hatchery_hits[:5]))

    if prevention:
        labels.append("biosecurity_management")
        evidence.append("field: prevention")
    else:
        bio_hits = contains_any(normalize_text(" ".join([title, summary, production])), biosecurity_keywords)
        if bio_hits:
            labels.append("biosecurity_management")
            evidence.append("biosecurity/management keywords: " + ", ".join(bio_hits[:5]))

    env_hits = contains_any(normalize_text(" ".join([title, summary, location, production])), environment_keywords)
    if env_hits:
        labels.append("environment_water_quality")
        evidence.append("environment keywords/fields: " + ", ".join(env_hits[:5]))

    local_hits = contains_any(normalize_text(" ".join([location, title, summary, source])), local_keywords)
    if local_hits:
        labels.append("local_vietnam_khanhhoa")
        evidence.append("local keywords/fields: " + ", ".join(local_hits[:5]))

    if taxon:
        labels.append("species_taxon_specific")
        evidence.append("field: related_taxon/species")
    else:
        species_hits = contains_any(normalize_text(" ".join([title, summary])), species_keywords)
        if species_hits:
            labels.append("species_taxon_specific")
            evidence.append("species/taxon keywords: " + ", ".join(species_hits[:5]))

    labels = list(dict.fromkeys(labels))

    if not labels:
        general_hits = contains_any(all_text, general_keywords)
        if general_hits:
            labels.append("general_policy_technical")
            evidence.append("general technical/policy keywords: " + ", ".join(general_hits[:5]))
        else:
            labels.append("uncategorized")
            evidence.append("no topic rule matched")

    location_text = location
    return labels, evidence, location_text


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def pct(n: int, total: int) -> float:
    return round((n / total * 100.0) if total else 0.0, 2)


def md_table(rows: list[dict[str, Any]], columns: list[str], max_rows: int | None = None) -> str:
    selected = rows[:max_rows] if max_rows else rows
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in selected:
        values = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                value = f"{value:.2f}"
            values.append(str(value).replace("|", "/").replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def create_figure(topic_rows: list[dict[str, Any]]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    rows = [r for r in topic_rows if r["topic_group"] != "uncategorized"]
    rows = sorted(rows, key=lambda r: int(r["n_documents"]))
    labels = [r["topic_group"] for r in rows]
    values = [int(r["n_documents"]) for r in rows]

    plt.figure(figsize=(10, 5.8))
    bars = plt.barh(labels, values, color="#3b6ea8", edgecolor="#1f2d3d", linewidth=0.7)
    plt.title("Corpus topic distribution")
    plt.xlabel("Number of documents")
    plt.grid(axis="x", alpha=0.25)
    for bar, value in zip(bars, values):
        plt.text(value + 0.8, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=9)
    plt.xlim(0, max(values + [1]) * 1.15)
    plt.tight_layout()
    plt.savefig(FIG_PATH, dpi=200)
    plt.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    if not METADATA_PATH.exists():
        raise FileNotFoundError(METADATA_PATH)

    df = pd.read_excel(METADATA_PATH)
    columns = list(df.columns)
    total_docs = len(df)

    cols = {
        "doc_id": detect_column(columns, ["doc_id", "document_id", "id"]),
        "title": detect_column(columns, ["title", "document_title"]),
        "source": detect_column(columns, ["source", "publisher", "journal"]),
        "year": detect_column(columns, ["year", "publishedYear", "published_year", "publication_year"]),
        "doc_type": detect_column(columns, ["doc_type", "docType", "type", "document_type"]),
        "taxon": detect_column(columns, ["taxon", "species", "related_taxon", "related_species"]),
        "disease": detect_column(columns, ["disease", "related_disease"]),
        "pathogen": detect_column(columns, ["pathogen", "related_pathogen"]),
        "symptom": detect_column(columns, ["symptom", "symptoms"]),
        "prevention": detect_column(columns, ["prevention", "recommended_prevention"]),
        "treatment": detect_column(columns, ["treatment", "recommended_treatment"]),
        "production_mode": detect_column(columns, ["production_mode", "mode", "production"]),
        "location": detect_column(columns, ["location", "related_location"]),
        "country": detect_column(columns, ["country"]),
        "region": detect_column(columns, ["region"]),
        "language": detect_column(columns, ["language", "lang"]),
        "summary": detect_column(columns, ["summary", "abstract", "description"]),
        "keywords": detect_column(columns, ["keywords", "keyword"]),
        "notes": detect_column(columns, ["notes", "note"]),
        "file_path": detect_column(columns, ["file_path", "path"]),
        "url": detect_column(columns, ["url", "referenceUrl", "reference_url"]),
    }
    missing = [k for k, v in cols.items() if v is None and k in {"pathogen", "symptom", "prevention", "treatment", "country", "region", "summary"}]

    doc_rows: list[dict[str, Any]] = []
    topic_docs: dict[str, set[str]] = defaultdict(set)
    source_topic_docs: dict[tuple[str, str], set[str]] = defaultdict(set)
    source_docs: Counter[str] = Counter()
    doc_type_docs: Counter[str] = Counter()
    language_docs: Counter[str] = Counter()
    location_docs: dict[str, set[str]] = defaultdict(set)

    for _, pd_row in df.iterrows():
        row = pd_row.to_dict()
        doc_id = clean(row.get(cols["doc_id"], "")) if cols["doc_id"] else f"doc_{len(doc_rows)+1:03d}"
        title = clean(row.get(cols["title"], "")) if cols["title"] else ""
        source = source_group(row, cols["source"], cols["doc_id"])
        year = clean(row.get(cols["year"], "")) if cols["year"] else ""
        doc_type = clean(row.get(cols["doc_type"], "")) if cols["doc_type"] else ""
        language = clean(row.get(cols["language"], "")) if cols["language"] else ""
        labels, evidence, location_text = classify_document(row, cols)

        source_docs[source] += 1
        if doc_type:
            doc_type_docs[doc_type] += 1
        if language:
            language_docs[language] += 1
        for label in labels:
            topic_docs[label].add(doc_id)
            source_topic_docs[(source, label)].add(doc_id)

        loc_parts = split_multi(location_text)
        if "local_vietnam_khanhhoa" in labels:
            location_docs["Vietnam/local-related"].add(doc_id)
        for loc in loc_parts:
            location_docs[loc].add(doc_id)

        notes = ""
        if "uncategorized" in labels:
            notes = "needs manual review"
        elif len(labels) > 1:
            notes = "multi-label"

        doc_rows.append(
            {
                "doc_id": doc_id,
                "title": title,
                "source": source,
                "year": year,
                "doc_type": doc_type,
                "topic_groups": "; ".join(labels),
                "n_topic_groups": len([x for x in labels if x != "uncategorized"]),
                "matched_keywords_or_fields": "; ".join(evidence),
                "location": location_text,
                "language": language,
                "notes": notes,
            }
        )

    topic_rows = []
    for topic in TOPIC_ORDER:
        docs = topic_docs.get(topic, set())
        notes = "multi-label count; total across topics can exceed corpus size"
        if topic == "uncategorized":
            notes = "documents not matched by topic rules; inspect manually"
        topic_rows.append(
            {
                "topic_group": topic,
                "n_documents": len(docs),
                "percentage_of_corpus": pct(len(docs), total_docs),
                "notes": notes,
            }
        )

    source_rows = []
    for (source, topic), docs in sorted(source_topic_docs.items(), key=lambda x: (x[0][0], TOPIC_ORDER.index(x[0][1]) if x[0][1] in TOPIC_ORDER else 999)):
        source_rows.append({"source": source, "topic_group": topic, "n_documents": len(docs)})

    location_rows = []
    for loc, docs in sorted(location_docs.items(), key=lambda x: (-len(x[1]), x[0])):
        note = "derived local flag" if loc == "Vietnam/local-related" else "from related_location metadata"
        location_rows.append({"location_or_region": loc, "n_documents": len(docs), "notes": note})

    write_csv(TOPIC_CSV, topic_rows, ["topic_group", "n_documents", "percentage_of_corpus", "notes"])
    write_csv(SOURCE_CSV, source_rows, ["source", "topic_group", "n_documents"])
    write_csv(LOCATION_CSV, location_rows, ["location_or_region", "n_documents", "notes"])
    write_csv(DOC_LABELS_CSV, doc_rows, ["doc_id", "title", "source", "year", "doc_type", "topic_groups", "n_topic_groups", "matched_keywords_or_fields", "location", "language", "notes"])
    create_figure(topic_rows)

    write_report(
        total_docs=total_docs,
        columns=columns,
        cols=cols,
        missing=missing,
        topic_rows=topic_rows,
        source_docs=source_docs,
        doc_type_docs=doc_type_docs,
        language_docs=language_docs,
        location_rows=location_rows,
        doc_rows=doc_rows,
        source_rows=source_rows,
    )

    print(f"[OK] documents={total_docs}")
    print(f"[OK] wrote {TOPIC_CSV.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {SOURCE_CSV.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {LOCATION_CSV.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {DOC_LABELS_CSV.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {REPORT_MD.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {FIG_PATH.relative_to(PROJECT_ROOT)}")


def write_report(
    total_docs: int,
    columns: list[str],
    cols: dict[str, str | None],
    missing: list[str],
    topic_rows: list[dict[str, Any]],
    source_docs: Counter[str],
    doc_type_docs: Counter[str],
    language_docs: Counter[str],
    location_rows: list[dict[str, Any]],
    doc_rows: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
) -> None:
    non_uncat = [r for r in topic_rows if r["topic_group"] != "uncategorized"]
    strongest = max(non_uncat, key=lambda r: int(r["n_documents"])) if non_uncat else {}
    weakest_candidates = [r for r in non_uncat if int(r["n_documents"]) > 0]
    weakest = min(weakest_candidates, key=lambda r: int(r["n_documents"])) if weakest_candidates else {}
    uncategorized = next((r for r in topic_rows if r["topic_group"] == "uncategorized"), {"n_documents": 0})
    multi_label_count = sum(1 for r in doc_rows if int(r["n_topic_groups"]) > 1)
    local_count = next((r["n_documents"] for r in topic_rows if r["topic_group"] == "local_vietnam_khanhhoa"), 0)
    top_topics = sorted(non_uncat, key=lambda r: int(r["n_documents"]), reverse=True)[:5]

    source_table = [
        {"source": source, "n_documents": count, "percentage": pct(count, total_docs)}
        for source, count in source_docs.most_common()
    ]
    doc_type_table = [
        {"doc_type": name, "n_documents": count, "percentage": pct(count, total_docs)}
        for name, count in doc_type_docs.most_common(12)
    ]
    language_table = [
        {"language": name, "n_documents": count, "percentage": pct(count, total_docs)}
        for name, count in language_docs.most_common()
    ]
    report_topic_rows = [
        {
            "Nhóm chủ đề": r["topic_group"],
            "Số tài liệu": r["n_documents"],
            "Tỷ lệ (%)": r["percentage_of_corpus"],
            "Ý nghĩa trong đánh giá": topic_meaning(r["topic_group"]),
        }
        for r in topic_rows
        if r["topic_group"] != "uncategorized"
    ]
    col_map_rows = [{"field": k, "detected_column": v or "MISSING"} for k, v in cols.items()]
    missing_text = ", ".join(missing) if missing else "Không có thiếu cột quan trọng cho thống kê chính; một số cột nâng cao vẫn có thể vắng mặt."
    top_topic_sentence = ", ".join(
        f"{r['topic_group']} ({r['n_documents']} tài liệu, {r['percentage_of_corpus']}%)"
        for r in top_topics
    )

    report = f"""# Corpus topic distribution report

Generated at: `2026-05-29`

## 1. Mục tiêu

Report này thống kê corpus theo nhóm chủ đề để kiểm tra dữ liệu có bị lệch quá nhiều về một nhóm hay không. Mục tiêu là cung cấp bằng chứng định lượng cho phần mô tả dữ liệu trong báo cáo đồ án, đồng thời chỉ ra các nhóm còn mỏng để đưa vào hạn chế/hướng phát triển.

## 2. Dữ liệu đầu vào

- Metadata file: `data/metadata/document_metadata_cleaned.xlsx`
- Tổng số tài liệu: **{total_docs}**
- Số cột metadata phát hiện: **{len(columns)}**
- Các cột metadata: `{", ".join(columns)}`

Mapping cột được dùng:

{md_table(col_map_rows, ["field", "detected_column"])}

Cột thiếu/không có trong metadata hiện tại: {missing_text}

## 3. Phương pháp phân loại topic

Phân loại được thực hiện theo hướng multi-label: một tài liệu có thể thuộc nhiều nhóm chủ đề cùng lúc. Ví dụ một manual về AHPND trong hatchery tôm có thể đồng thời thuộc `aquatic_disease`, `hatchery_seed_production`, `biosecurity_management` và `species_taxon_specific`.

Topic group được xác định bằng cách kết hợp metadata fields (`related_taxon`, `related_disease`, `related_location`, `production_mode`, `keywords`, `docType`, `language`) và keyword trong title/note/keywords. Đây là thống kê hỗ trợ báo cáo, không phải annotation chủ đề hoàn hảo. Tổng count theo topic vì vậy có thể lớn hơn tổng số tài liệu.

## 4. Kết quả tổng thể theo topic group

{md_table(topic_rows, ["topic_group", "n_documents", "percentage_of_corpus", "notes"])}

Số tài liệu multi-label: **{multi_label_count}/{total_docs}**. Số tài liệu chưa phân loại được: **{uncategorized.get("n_documents", 0)}**.

## 5. Phân bố theo nguồn tài liệu

Phân bố theo source group:

{md_table(source_table, ["source", "n_documents", "percentage"])}

Phân bố source-topic chi tiết được lưu tại `outputs/corpus_topic_distribution_by_source.csv`. Nhìn chung, source group lớn nhất là **{source_docs.most_common(1)[0][0]}** với **{source_docs.most_common(1)[0][1]}** tài liệu. Corpus cũng có nhóm tài liệu từ journal/PMC-style, SEAFDEC, NACA, RIA3 và tài liệu tiếng Việt như TB/TCTS nếu metadata có nguồn tương ứng.

Doc type phổ biến:

{md_table(doc_type_table, ["doc_type", "n_documents", "percentage"])}

Language:

{md_table(language_table, ["language", "n_documents", "percentage"])}

## 6. Phân bố tài liệu địa phương

Số tài liệu thuộc nhóm `local_vietnam_khanhhoa`: **{local_count}**. Bảng location/top region:

{md_table(location_rows, ["location_or_region", "n_documents", "notes"], max_rows=20)}

File đầy đủ: `outputs/corpus_topic_distribution_by_location.csv`.

## 7. Nhận xét về độ cân bằng dữ liệu

Corpus có bao phủ nhiều nhóm chủ đề khác nhau, đặc biệt các nhóm nổi bật là {top_topic_sentence}. Nhóm nhiều nhất là **{strongest.get("topic_group", "N/A")}** với **{strongest.get("n_documents", 0)}** tài liệu, phản ánh trọng tâm của corpus vào các tài liệu có taxon/loài cụ thể và tài liệu bệnh/quản lý sức khỏe thủy sản. Nhóm ít nhất trong các nhóm có tài liệu là **{weakest.get("topic_group", "N/A")}** với **{weakest.get("n_documents", 0)}** tài liệu.

Không nên diễn giải corpus là hoàn toàn cân bằng, vì phân bố vẫn chịu ảnh hưởng bởi nguồn thu thập và trọng tâm bài toán shrimp disease/biosecurity. Tuy vậy, thống kê multi-label cho thấy dữ liệu không chỉ tập trung vào một nhóm duy nhất mà có độ phủ qua disease, hatchery, management, environment, local và species/taxon. Các nhóm có số lượng thấp hơn nên được xem là hạn chế và hướng bổ sung dữ liệu nếu phát triển hệ thống quy mô lớn hơn.

## 8. Đoạn có thể chèn vào báo cáo

Corpus cuối cùng của đề tài gồm **{total_docs}** tài liệu, được thống kê theo các nhóm chủ đề chính bằng phương pháp multi-label dựa trên metadata và keyword trong title/notes. Kết quả cho thấy các nhóm có số lượng nổi bật gồm {top_topic_sentence}. Nhóm `local_vietnam_khanhhoa` có **{local_count}** tài liệu, phản ánh sự hiện diện của tài liệu Việt Nam/Khánh Hòa/ĐBSCL và các vùng nuôi liên quan. Do cách phân loại là multi-label, một tài liệu có thể thuộc nhiều nhóm nên tổng số count theo nhóm có thể lớn hơn **{total_docs}**. Thống kê này cho thấy corpus không bị lệch hoàn toàn vào một nhóm duy nhất, mà có độ bao phủ nhất định giữa bệnh thủy sản, nuôi/trại giống, quản lý an toàn sinh học, môi trường và tài liệu địa phương. Tuy nhiên, phân bố chưa thể xem là cân bằng tuyệt đối; các nhóm có số lượng thấp hơn cần được bổ sung nếu mở rộng đề tài thành hệ thống retrieval chuyên sâu hơn.

## 9. Bảng gợi ý đưa vào báo cáo

{md_table(report_topic_rows, ["Nhóm chủ đề", "Số tài liệu", "Tỷ lệ (%)", "Ý nghĩa trong đánh giá"])}

## 10. Hạn chế

- Thống kê dựa trên metadata/keyword nên có thể chưa hoàn hảo.
- Một số tài liệu có thể bị thiếu hoặc dư topic label nếu metadata chưa đầy đủ hoặc title quá chung.
- `general_policy_technical` chỉ được gán khi tài liệu không rơi rõ vào các nhóm chuyên đề khác.
- Nếu muốn dùng phân bố chủ đề như benchmark học thuật, cần kiểm tra thủ công hoặc gán topic label riêng bởi annotator.
- Vì là multi-label, tổng count theo topic không tương ứng với số tài liệu duy nhất.

## 11. Safety confirmation

- Không sửa metadata gốc.
- Không sửa ontology/runtime/scoring.
- Không sửa query set/relevance judgments/baseline results/metrics.
- Chỉ tạo output thống kê mới trong `outputs/`, `outputs/figures/` và script trong `experiments/`.

## 12. Outputs

- `outputs/corpus_topic_distribution.csv`
- `outputs/corpus_topic_distribution_by_source.csv`
- `outputs/corpus_topic_distribution_by_location.csv`
- `outputs/corpus_topic_distribution_document_labels.csv`
- `outputs/corpus_topic_distribution_report.md`
- `outputs/figures/fig_corpus_topic_distribution.png`
"""
    REPORT_MD.write_text(report, encoding="utf-8")


def topic_meaning(topic: str) -> str:
    return {
        "aquatic_disease": "Đánh giá truy vấn bệnh, pathogen, diagnosis và disease control.",
        "marine_aquaculture": "Đánh giá truy vấn nuôi biển, lobster/coastal aquaculture.",
        "hatchery_seed_production": "Đánh giá truy vấn hatchery, seed, larvae, broodstock.",
        "biosecurity_management": "Đánh giá truy vấn biosecurity, prevention, risk và health management.",
        "environment_water_quality": "Đánh giá truy vấn môi trường, quan trắc và water quality.",
        "local_vietnam_khanhhoa": "Đánh giá truy vấn địa phương Việt Nam/Khánh Hòa/ĐBSCL.",
        "species_taxon_specific": "Đánh giá truy vấn theo loài/taxon như shrimp, lobster, Penaeus.",
        "general_policy_technical": "Bổ sung tài liệu chính sách/kỹ thuật/tổng quan.",
    }.get(topic, "")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise
