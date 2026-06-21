from __future__ import annotations

from io import BytesIO
from contextlib import contextmanager
from html import escape
from pathlib import Path
import re
from typing import Any

try:
    import streamlit as st
except ModuleNotFoundError as exc:  # pragma: no cover - user-facing dependency message
    raise SystemExit(
        "Streamlit is not installed. Install it with: python -m pip install streamlit"
    ) from exc

import pandas as pd

import hybrid_search
from hybrid_search import (
    METADATA_PATH,
    build_metadata_lookup,
    build_term_index,
    load_full_metadata,
)
from vector_search import load_index


APP_TITLE = "Aquaculture Semantic Search Demo"
EXAMPLE_QUERIES = [
    "AHPND shrimp disease",
    "lobster Khanh Hoa",
    "shrimp farming Vietnam",
    "biosecurity shrimp hatchery",
]

METHOD_OPTIONS = [
    "Hybrid",
    "Vector",
    "Vector + metadata",
    "Ontology/SPARQL",
    "Lexical/BM25",
]

ACTIVE_METHODS = {"Hybrid", "Vector", "Vector + metadata"}
OFFLINE_FALLBACK_METHODS = {"Ontology/SPARQL", "Lexical/BM25"}

SNAPSHOT_CORE_QUERIES = 28

OFFLINE_BASELINE_FILES = {
    "Lexical/BM25": [
        Path("data/eval/results/baseline_lexical_core.csv"),
        Path("data/eval/results/baseline_lexical_extended.csv"),
    ],
    "Ontology/SPARQL": [
        Path("data/eval/results/baseline_ontology_sparql_core.csv"),
        Path("data/eval/results/baseline_ontology_sparql_extended.csv"),
    ],
}

SNIPPET_KEYS = [
    "snippet",
    "relevant_snippet",
    "chunk_text",
    "text",
    "content",
    "summary",
    "abstract",
]
SOURCE_KEYS = [
    "file_path",
    "source",
    "referenceUrl",
    "reference_url",
    "url",
    "doc_url",
    "path",
]
PAGE_KEYS = ["page", "page_number", "page_start", "page_end", "pages"]
CHUNK_KEYS = ["chunk_id", "chunk_index", "chunk", "record_id"]


@st.cache_resource(show_spinner="Loading vector index, metadata, and KG runtime...")
def load_runtime_resources():
    model, index, records = load_index()
    metadata_df = load_full_metadata(METADATA_PATH)
    metadata_lookup = build_metadata_lookup(metadata_df)
    term_index = build_term_index(metadata_df)
    return model, index, records, metadata_lookup, term_index


@contextmanager
def temporary_top_k(top_k: int):
    original_final_k = hybrid_search.FINAL_K
    try:
        hybrid_search.FINAL_K = int(top_k)
        yield
    finally:
        hybrid_search.FINAL_K = original_final_k


def safe_get(item: Any, possible_keys: str | list[str] | tuple[str, ...], default: Any = "N/A") -> Any:
    keys = [possible_keys] if isinstance(possible_keys, str) else list(possible_keys)
    for key in keys:
        value = None
        found = False
        if isinstance(item, dict):
            if key in item:
                value = item.get(key)
                found = True
        else:
            if hasattr(item, key):
                value = getattr(item, key)
                found = True
        if found and value is not None and value != "":
            return value
    return default


def metadata_get(metadata_lookup: dict[str, dict], doc_id: str, possible_keys: str | list[str], default: Any = "N/A") -> Any:
    row = metadata_lookup.get(str(doc_id), {}) or {}
    return safe_get(row, possible_keys, default=default)


def first_available(item: Any, metadata_lookup: dict[str, dict] | None, doc_id: str, keys: list[str]) -> Any:
    value = safe_get(item, keys, default="")
    if value != "":
        return value
    if metadata_lookup is not None:
        return metadata_get(metadata_lookup, doc_id, keys, default="")
    return ""


def format_score(value: Any) -> str:
    if value is None or value == "":
        return "N/A"
    try:
        return f"{float(value):.4f}"
    except Exception:
        return str(value)


def score_or_na(item: Any, possible_keys: str | list[str] | tuple[str, ...]) -> str:
    return format_score(safe_get(item, possible_keys, default=""))


def truncate_text(text: Any, max_chars: int = 400) -> str:
    if text is None or text == "":
        return ""
    value = " ".join(str(text).split())
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def metadata_text(metadata_lookup: dict[str, dict], doc_id: str, field: str) -> str:
    row = metadata_lookup.get(doc_id, {}) or {}
    return str(row.get(field, "") or "")


def apply_post_filters(results: list[Any], metadata_lookup: dict[str, dict], filters: dict[str, str]) -> list[Any]:
    filtered = []
    field_map = {
        "disease": "related_disease",
        "species": "related_taxon",
        "location": "related_location",
        "source": "source",
    }
    for item in results:
        doc_id = str(safe_get(item, "doc_id", default=""))
        keep = True
        for filter_key, filter_value in filters.items():
            if not filter_value.strip():
                continue
            haystack = metadata_text(metadata_lookup, doc_id, field_map[filter_key]).lower()
            if filter_value.strip().lower() not in haystack:
                keep = False
                break
        if keep:
            filtered.append(item)
    return filtered


def result_table_rows(results: list[Any], metadata_lookup: dict[str, dict]) -> list[dict[str, Any]]:
    rows = []
    for rank, item in enumerate(results, start=1):
        doc_id = str(safe_get(item, "doc_id", default=""))
        source = first_available(item, metadata_lookup, doc_id, ["source"])
        file_path = first_available(item, metadata_lookup, doc_id, ["file_path", "path"])
        rows.append(
            {
                "rank": rank,
                "doc_id": safe_get(item, "doc_id"),
                "title": first_available(item, metadata_lookup, doc_id, ["title"]),
                "final_score": score_or_na(item, ["final_score", "score"]),
                "score_raw": score_or_na(item, ["score_raw", "final_score", "score"]),
                "vector_score": score_or_na(item, ["vector_score", "score"]),
                "metadata_delta": score_or_na(item, ["metadata_delta", "kg_bonus"]),
                "kg_score": score_or_na(item, "kg_score"),
                "intent_adjustment": score_or_na(item, "intent_adjustment"),
                "source": truncate_text(source, max_chars=70) if source else "N/A",
                "file_path": truncate_text(file_path, max_chars=90) if file_path else "N/A",
                "method": safe_get(item, "method", default=""),
            }
        )
    return rows


def compact_result_table_rows(results: list[Any], metadata_lookup: dict[str, dict]) -> list[dict[str, Any]]:
    rows = []
    for row in result_table_rows(results, metadata_lookup):
        rows.append(
            {
                "rank": row["rank"],
                "doc_id": row["doc_id"],
                "title": row["title"],
                "final_score": row["final_score"],
                "kg_score": row["kg_score"],
                "source": row["source"],
            }
        )
    return rows


def comparison_table_rows(results: list[Any], metadata_lookup: dict[str, dict]) -> list[dict[str, Any]]:
    rows = []
    for row in result_table_rows(results, metadata_lookup):
        rows.append(
            {
                "rank": row["rank"],
                "doc_id": row["doc_id"],
                "title": row["title"],
                "score": row["final_score"],
            }
        )
    return rows


def comparison_display_rows(
    results: list[Any],
    metadata_lookup: dict[str, dict],
    method_name: str,
) -> list[dict[str, Any]]:
    rows = result_table_rows(results, metadata_lookup)
    if method_name == "Hybrid":
        columns = ["rank", "doc_id", "title", "final_score", "kg_score", "source"]
    elif method_name == "Vector":
        columns = ["rank", "doc_id", "title", "vector_score", "source", "file_path"]
    elif method_name == "Vector + metadata":
        columns = ["rank", "doc_id", "title", "final_score", "vector_score", "metadata_delta", "source"]
    else:
        columns = ["rank", "doc_id", "title", "final_score"]
    return [{col: row.get(col, "N/A") for col in columns if col in row} for row in rows]


def render_html_table(rows: list[dict[str, Any]], numeric_columns: set[str] | None = None) -> None:
    if not rows:
        st.info("No rows available.")
        return
    numeric_columns = numeric_columns or set()
    columns = list(rows[0].keys())
    header = "".join(f"<th>{escape(str(col))}</th>" for col in columns)
    body_rows = []
    for row in rows:
        cells = []
        for col in columns:
            value = row.get(col, "N/A")
            css_class = "num" if col in numeric_columns else "text"
            cells.append(f'<td class="{css_class}">{escape(str(value))}</td>')
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown(
        f"""
        <div class="topk-table-wrap">
            <table class="topk-table">
                <thead><tr>{header}</tr></thead>
                <tbody>{''.join(body_rows)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_comparison_table(rows: list[dict[str, Any]] | None, method_name: str) -> None:
    if rows is None:
        st.info(f"{method_name} comparison is unavailable for the current query.")
        return
    df = pd.DataFrame(rows)
    if df.empty:
        st.info(f"No {method_name} comparison results available. Run a search first or choose another method.")
        return
    preferred_columns = {
        "Hybrid": ["rank", "doc_id", "title", "final_score", "kg_score", "source"],
        "Vector": ["rank", "doc_id", "title", "vector_score", "source", "file_path"],
        "Vector + metadata": ["rank", "doc_id", "title", "final_score", "vector_score", "metadata_delta", "source"],
        "Ontology/SPARQL": ["rank", "doc_id", "title", "score_raw", "source", "method"],
        "Lexical/BM25": ["rank", "doc_id", "title", "score_raw", "source", "method"],
    }.get(method_name, list(df.columns))
    display_columns = [col for col in preferred_columns if col in df.columns]
    if not display_columns:
        st.info(f"No displayable {method_name} comparison columns are available.")
        return
    display_df = df[display_columns].fillna("N/A")
    render_html_table(
        display_df.to_dict(orient="records"),
        numeric_columns={"rank", "final_score", "vector_score", "metadata_delta", "kg_score", "score", "score_raw"},
    )


def render_topk_table(results: list[Any], metadata_lookup: dict[str, dict]) -> None:
    rows = compact_result_table_rows(results, metadata_lookup)
    if not rows:
        st.info("No Top-k rows to display.")
        return

    columns = [
        "rank",
        "doc_id",
        "title",
        "final_score",
        "kg_score",
        "source",
    ]
    numeric_cols = {
        "rank",
        "final_score",
        "vector_score",
        "metadata_delta",
        "kg_score",
        "intent_adjustment",
    }
    header = "".join(f"<th>{escape(col)}</th>" for col in columns)
    body_rows = []
    for row in rows:
        cells = []
        for col in columns:
            value = row.get(col, "N/A")
            css_class = "num" if col in numeric_cols else "text"
            cells.append(f'<td class="{css_class}">{escape(str(value))}</td>')
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    st.markdown(
        f"""
        <div class="topk-table-wrap">
            <table class="topk-table">
                <thead><tr>{header}</tr></thead>
                <tbody>{''.join(body_rows)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def entity_rows(detected: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not isinstance(detected, dict):
        return rows
    for entity_type, values in detected.items():
        if not values:
            continue
        if not isinstance(values, list):
            values = [values]
        for value in values:
            if isinstance(value, dict):
                canonical = safe_get(value, ["canonical", "label", "name"], default="")
                alias = safe_get(value, ["alias", "matched_alias"], default="")
                kg_uri = safe_get(value, ["kg_uri", "uri"], default="")
            else:
                canonical = str(value)
                alias = ""
                kg_uri = ""
            rows.append(
                {
                    "Entity type": str(entity_type),
                    "Canonical/label": str(canonical or "N/A"),
                    "Matched alias": str(alias or "N/A"),
                    "KG URI": str(kg_uri or "N/A"),
                }
            )
    return rows


def entity_labels(detected: Any, key: str) -> str:
    if not isinstance(detected, dict):
        return "N/A"
    values = detected.get(key) or []
    if not isinstance(values, list):
        values = [values]
    labels = []
    for value in values:
        if isinstance(value, dict):
            label = safe_get(value, ["canonical", "label", "name"], default="")
        else:
            label = str(value)
        if label:
            labels.append(str(label))
    return "; ".join(dict.fromkeys(labels)) if labels else "N/A"


def render_detected_entities(detected: Any) -> None:
    cards = st.columns(5)
    cards[0].metric("Taxon/species", entity_labels(detected, "species"))
    cards[1].metric("Disease", entity_labels(detected, "disease"))
    cards[2].metric("Location", entity_labels(detected, "location"))
    cards[3].metric("Production mode", entity_labels(detected, "mode"))
    cards[4].metric("Intent/type", entity_labels(detected, "topic"))
    rows = entity_rows(detected)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No explicit entity detected; system relies more on vector and metadata matching.")
    with st.expander("Raw entities"):
        st.json(detected if detected else {"entities": "N/A"}, expanded=False)


def split_entity_values(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = re.split(r";|\||\n", str(value))
    cleaned = []
    for raw in raw_values:
        text = " ".join(str(raw).split()).strip(" ,")
        if text and text.lower() not in {"nan", "none", "n/a"}:
            cleaned.append(text)
    return list(dict.fromkeys(cleaned))


def source_evidence(item: Any, metadata_lookup: dict[str, dict]) -> tuple[str, str]:
    doc_id = str(safe_get(item, "doc_id", default=""))
    snippet = truncate_text(first_available(item, metadata_lookup, doc_id, SNIPPET_KEYS), max_chars=450)
    source = first_available(item, metadata_lookup, doc_id, SOURCE_KEYS)
    return snippet, str(source or "")


def source_evidence_rows(item: Any, metadata_lookup: dict[str, dict]) -> tuple[list[dict[str, Any]], str]:
    doc_id = str(safe_get(item, "doc_id", default=""))
    title = first_available(item, metadata_lookup, doc_id, ["title"])
    source = first_available(item, metadata_lookup, doc_id, ["source"])
    file_path = first_available(item, metadata_lookup, doc_id, ["file_path", "path"])
    reference_url = first_available(item, metadata_lookup, doc_id, ["referenceUrl", "reference_url", "url"])
    page = first_available(item, metadata_lookup, doc_id, PAGE_KEYS)
    chunk = first_available(item, metadata_lookup, doc_id, CHUNK_KEYS)
    snippet = truncate_text(first_available(item, metadata_lookup, doc_id, SNIPPET_KEYS), max_chars=900)

    raw_rows = [
        ("doc_id", doc_id),
        ("title", title),
        ("source", source),
        ("file_path", file_path),
        ("referenceUrl", reference_url),
        ("page", page),
        ("chunk", chunk),
    ]
    rows = []
    for field, value in raw_rows:
        if value is None:
            continue
        if isinstance(value, str) and value == "":
            continue
        rows.append({"field": field, "value": value})
    if snippet:
        rows.append({"field": "snippet/source_evidence", "value": snippet})
    return rows, snippet


def render_source_evidence(item: Any, metadata_lookup: dict[str, dict]) -> None:
    rows, snippet = source_evidence_rows(item, metadata_lookup)

    if snippet:
        st.markdown("**Source evidence / snippet**")
        st.markdown(f'<div class="snippet">{escape(snippet)}</div>', unsafe_allow_html=True)
    else:
        st.info("No source snippet was returned for this result.")

    st.markdown("**Source metadata**")
    if rows:
        render_html_table(rows, numeric_columns=set())
    else:
        st.info("No source metadata was returned for this result.")


def render_score_boxes(item: Any) -> None:
    cols = st.columns(5)
    cols[0].metric("Final score", score_or_na(item, ["final_score", "score"]))
    cols[1].metric("Vector", score_or_na(item, ["vector_score", "score"]))
    cols[2].metric("Metadata", score_or_na(item, ["metadata_delta", "kg_bonus"]))
    cols[3].metric("KG", score_or_na(item, "kg_score"))
    cols[4].metric("Intent", score_or_na(item, "intent_adjustment"))


def detail_score_fields(item: Any) -> dict[str, Any]:
    return {
        "final_score": safe_get(item, ["final_score", "score"]),
        "vector_score": safe_get(item, ["vector_score", "score"]),
        "metadata_delta": safe_get(item, ["metadata_delta", "kg_bonus"]),
        "kg_score": safe_get(item, "kg_score"),
        "intent_adjustment": safe_get(item, "intent_adjustment"),
        "kg_bonus_breakdown": safe_get(item, "kg_bonus_breakdown"),
        "kg_penalty_breakdown": safe_get(item, "kg_penalty_breakdown"),
        "bonus_breakdown": safe_get(item, "bonus_breakdown"),
        "penalty_breakdown": safe_get(item, "penalty_breakdown"),
        "doc_uri_in_kg": safe_get(item, "doc_uri_in_kg"),
    }


def kg_explanation_text(item: Any) -> str:
    kg_explanation = safe_get(item, "kg_explanation", default="")
    if isinstance(kg_explanation, list):
        return "\n".join(str(part) for part in kg_explanation if part)
    return str(kg_explanation or "")


def kg_evidence_summary(item: Any, metadata_lookup: dict[str, dict], detected: Any | None = None) -> str:
    doc_id = str(safe_get(item, "doc_id", default=""))
    parts = [
        f"kg_score={safe_get(item, 'kg_score', default='N/A')}",
        f"doc_uri={safe_get(item, 'doc_uri_in_kg', default='N/A')}",
    ]
    for field in ["kg_bonus_breakdown", "kg_penalty_breakdown"]:
        value = safe_get(item, field, default="")
        if value:
            parts.append(f"{field}={value}")
    row = metadata_lookup.get(doc_id, {}) or {}
    for field in ["related_disease", "related_taxon", "related_location", "production_mode"]:
        values = split_entity_values(row.get(field, ""))
        if values:
            parts.append(f"{field}={'; '.join(values[:5])}")
    if detected:
        parts.append(f"detected_entities={entity_rows(detected)}")
    return " | ".join(parts)


def build_kg_evidence_rows(item: Any, metadata_lookup: dict[str, dict], detected: Any | None = None) -> list[dict[str, str]]:
    doc_id = str(safe_get(item, "doc_id", default=""))
    subject = str(safe_get(item, "doc_uri_in_kg", default="")) or f"Document_{doc_id}"
    if subject == "N/A":
        subject = f"Document_{doc_id}"
    row = metadata_lookup.get(doc_id, {}) or {}
    predicate_map = {
        "related_disease": "aboutDisease",
        "related_taxon": "aboutTaxon",
        "related_location": "aboutLocation",
        "production_mode": "documentProductionMode",
    }
    evidence_rows: list[dict[str, str]] = []
    for field, predicate in predicate_map.items():
        for value in split_entity_values(row.get(field, "")):
            evidence_rows.append(
                {
                    "subject": subject,
                    "predicate": predicate,
                    "object": value,
                    "evidence_type": "metadata/document fact",
                }
            )

    kg_matched = safe_get(item, "kg_matched_entities", default={})
    if isinstance(kg_matched, dict):
        for bucket, values in kg_matched.items():
            for value in split_entity_values(values):
                evidence_rows.append(
                    {
                        "subject": "query",
                        "predicate": f"matched_{bucket}",
                        "object": value,
                        "evidence_type": "runtime matched entity",
                    }
                )

    if isinstance(detected, dict):
        for entity_type, values in detected.items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                label = safe_get(value, ["canonical", "label", "name"], default=value) if isinstance(value, dict) else value
                if label:
                    evidence_rows.append(
                        {
                            "subject": "query",
                            "predicate": f"detected_{entity_type}",
                            "object": str(label),
                            "evidence_type": "detected query entity",
                        }
                    )

    explanation = kg_explanation_text(item)
    for predicate in [
        "aboutDisease",
        "aboutTaxon",
        "aboutLocation",
        "documentProductionMode",
        "causedBy",
        "affectsTaxon",
        "relatedTaxon",
        "pathogen",
        "recommendedPrevention",
    ]:
        if predicate in explanation:
            evidence_rows.append(
                {
                    "subject": subject,
                    "predicate": predicate,
                    "object": "see KG explanation text",
                    "evidence_type": "parsed_from_explanation",
                }
            )
    return evidence_rows


def render_kg_evidence(item: Any, metadata_lookup: dict[str, dict], detected: Any | None = None) -> None:
    kg_fields = [
        {"field": "kg_score", "value": safe_get(item, "kg_score", default="N/A")},
        {"field": "kg_direct_match", "value": safe_get(item, "kg_direct_match", default="N/A")},
        {"field": "kg_relation_match", "value": safe_get(item, "kg_relation_match", default="N/A")},
        {"field": "kg_context_match", "value": safe_get(item, "kg_context_match", default="N/A")},
        {"field": "kg_bonus_breakdown", "value": safe_get(item, "kg_bonus_breakdown", default="N/A")},
        {"field": "kg_penalty_breakdown", "value": safe_get(item, "kg_penalty_breakdown", default="N/A")},
        {"field": "doc_uri_in_kg", "value": safe_get(item, "doc_uri_in_kg", default="N/A")},
    ]
    st.markdown("**KG score and evidence fields**")
    render_html_table(kg_fields, numeric_columns=set())

    explanation = kg_explanation_text(item)
    if explanation:
        st.markdown("**KG explanation**")
        st.markdown(f'<div class="explanation">{escape(explanation)}</div>', unsafe_allow_html=True)
    else:
        st.info("No KG explanation text was returned by runtime for this result.")

    evidence_rows = build_kg_evidence_rows(item, metadata_lookup, detected)
    st.markdown("**KG/document evidence rows**")
    if evidence_rows:
        render_html_table(evidence_rows, numeric_columns=set())
    else:
        st.info("No explicit KG relation rows were returned by runtime for this result.")


def result_option_label(rank: int, item: Any) -> str:
    doc_id = safe_get(item, "doc_id", default="N/A")
    title = truncate_text(safe_get(item, "title", default="N/A"), max_chars=80)
    return f"#{rank} - {doc_id} - {title}"


def render_result_details(results: list[Any], metadata_lookup: dict[str, dict], detected: Any | None = None) -> None:
    if not results:
        st.info("No result selected.")
        return
    labels = [result_option_label(i, item) for i, item in enumerate(results, start=1)]
    selected_label = st.selectbox("Select result for details", labels, index=0)
    selected_index = labels.index(selected_label)
    item = results[selected_index]
    doc_id = str(safe_get(item, "doc_id", default=""))
    title = first_available(item, metadata_lookup, doc_id, ["title"])

    st.markdown(
        f'<div class="result-title">{escape(str(doc_id))} | {escape(str(title))}</div>',
        unsafe_allow_html=True,
    )
    score_tab, explanation_tab, kg_tab, source_tab = st.tabs(
        ["Score breakdown", "Explanation", "KG evidence", "Source evidence"]
    )
    with score_tab:
        render_score_boxes(item)
        with st.expander("Detailed score fields"):
            st.json(detail_score_fields(item), expanded=False)
    with explanation_tab:
        explanation = safe_get(item, ["explanation", "kg_explanation"], default="N/A")
        explanation_text = str(explanation)
        if len(explanation_text) > 900:
            st.markdown(
                f'<div class="explanation">{escape(truncate_text(explanation_text, 900))}</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Full explanation"):
                st.write(explanation_text)
        else:
            st.markdown(f'<div class="explanation">{escape(explanation_text)}</div>', unsafe_allow_html=True)
    with kg_tab:
        render_kg_evidence(item, metadata_lookup, detected)
    with source_tab:
        render_source_evidence(item, metadata_lookup)


def render_result_cards(results: list[Any], metadata_lookup: dict[str, dict]) -> None:
    for rank, item in enumerate(results, start=1):
        doc_id = safe_get(item, "doc_id")
        title = safe_get(item, "title")
        snippet, source = source_evidence(item, metadata_lookup)

        with st.container(border=True):
            st.markdown(
                f'<div class="result-title">#{rank} | {escape(str(doc_id))} | {escape(str(title))}</div>',
                unsafe_allow_html=True,
            )
            render_score_boxes(item)

            explanation = safe_get(item, ["explanation", "kg_explanation"], default="N/A")
            st.markdown("**Explanation**")
            st.markdown(f'<div class="explanation">{escape(str(explanation))}</div>', unsafe_allow_html=True)

            st.markdown("**Source evidence**")
            if snippet:
                st.markdown(f'<div class="snippet">{escape(snippet)}</div>', unsafe_allow_html=True)
            if source:
                st.caption(f"Source: {source}")
            if not snippet and not source:
                st.caption("Source evidence: N/A")

            with st.expander("Detailed score fields"):
                detail_rows = {
                    "final_score": safe_get(item, ["final_score", "score"]),
                    "vector_score": safe_get(item, ["vector_score", "score"]),
                    "metadata_delta": safe_get(item, ["metadata_delta", "kg_bonus"]),
                    "kg_score": safe_get(item, "kg_score"),
                    "intent_adjustment": safe_get(item, "intent_adjustment"),
                    "kg_bonus_breakdown": safe_get(item, "kg_bonus_breakdown"),
                    "kg_penalty_breakdown": safe_get(item, "kg_penalty_breakdown"),
                    "bonus_breakdown": safe_get(item, "bonus_breakdown"),
                    "penalty_breakdown": safe_get(item, "penalty_breakdown"),
                    "doc_uri_in_kg": safe_get(item, "doc_uri_in_kg"),
                }
                st.json(detail_rows, expanded=False)


def aggregate_vector_hits_to_docs(hits: list[dict], metadata_lookup: dict[str, dict], top_k: int) -> list[dict]:
    best_by_doc: dict[str, dict] = {}
    for hit in hits:
        doc_id = str(hit.get("doc_id", ""))
        if not doc_id:
            continue
        score = float(hit.get("score", 0.0) or 0.0)
        previous = best_by_doc.get(doc_id)
        if previous is not None and score <= float(previous.get("final_score", 0.0)):
            continue
        item = hit.copy()
        item["title"] = first_available(item, metadata_lookup, doc_id, ["title"])
        item["vector_score"] = score
        item["metadata_delta"] = 0.0
        item["kg_score"] = 0.0
        item["intent_adjustment"] = 0.0
        item["final_score"] = score
        item["explanation"] = "Vector-only retrieval from the existing FAISS vector index."
        best_by_doc[doc_id] = item
    return sorted(best_by_doc.values(), key=lambda row: float(row.get("final_score", 0.0)), reverse=True)[:top_k]


def vector_metadata_search(
    query: str,
    model,
    index,
    records: list[dict],
    metadata_lookup: dict[str, dict],
    term_index: list[dict],
    top_k: int,
) -> tuple[dict, list[dict]]:
    detected = hybrid_search.detect_entities(query, term_index)
    candidate_k = max(int(top_k) * 10, int(getattr(hybrid_search, "CANDIDATE_K", top_k)))
    candidates = hybrid_search.vector_only_search(query, model, index, records, top_k=candidate_k)
    best_by_doc: dict[str, dict] = {}
    delta_cache: dict[str, dict] = {}

    for item in candidates:
        doc_id = str(item.get("doc_id", ""))
        if not doc_id:
            continue
        if doc_id not in delta_cache:
            row = metadata_lookup.get(doc_id, {})
            match_info = hybrid_search.compute_match_features(row, detected)
            delta_cache[doc_id] = hybrid_search.compute_hybrid_delta(detected, match_info)
        delta_info = delta_cache[doc_id]
        vector_score = float(item.get("score", 0.0) or 0.0)
        metadata_delta = float(delta_info.get("kg_delta", 0.0) or 0.0)
        final_score = vector_score + metadata_delta
        previous = best_by_doc.get(doc_id)
        if previous is not None and final_score <= float(previous.get("final_score", 0.0)):
            continue
        new_item = item.copy()
        new_item["title"] = first_available(new_item, metadata_lookup, doc_id, ["title"])
        new_item["vector_score"] = vector_score
        new_item["metadata_delta"] = metadata_delta
        new_item["kg_score"] = 0.0
        new_item["intent_adjustment"] = 0.0
        new_item["final_score"] = final_score
        new_item["explanation"] = delta_info.get("explanation", "Vector + metadata reranking.")
        best_by_doc[doc_id] = new_item

    results = sorted(best_by_doc.values(), key=lambda row: float(row.get("final_score", 0.0)), reverse=True)[:top_k]
    return detected, results


def normalize_query_for_match(value: Any) -> str:
    try:
        return hybrid_search.normalize_text(str(value or ""))
    except Exception:
        return " ".join(str(value or "").lower().split())


def offline_baseline_results(
    method: str,
    query: str,
    metadata_lookup: dict[str, dict],
    top_k: int,
) -> tuple[dict, list[dict], str]:
    paths = OFFLINE_BASELINE_FILES.get(method, [])
    if not paths:
        return {}, [], f"{method} has no configured offline baseline fallback."
    q_norm = normalize_query_for_match(query)
    checked_paths: list[str] = []
    for path in paths:
        checked_paths.append(str(path))
        if not path.exists():
            continue
        df = pd.read_csv(path, encoding="utf-8-sig")
        if "query_text" not in df.columns:
            continue
        match_mask = df["query_text"].map(normalize_query_for_match) == q_norm
        if not match_mask.any() and "query_id" in df.columns:
            match_mask = df["query_id"].map(normalize_query_for_match) == q_norm
        if not match_mask.any():
            continue
        matched = df[match_mask].copy()
        matched["rank_num"] = pd.to_numeric(matched.get("rank"), errors="coerce")
        matched = matched.sort_values("rank_num").head(int(top_k))
        rows: list[dict[str, Any]] = []
        for _, row in matched.iterrows():
            doc_id = str(row.get("doc_id", ""))
            score_raw = row.get("score_raw", row.get("score_normalized", ""))
            rows.append(
                {
                    "rank": int(row.get("rank", len(rows) + 1)),
                    "doc_id": doc_id,
                    "title": row.get("title", first_available({}, metadata_lookup, doc_id, ["title"])),
                    "score_raw": score_raw,
                    "score": score_raw,
                    "final_score": score_raw,
                    "source": first_available({}, metadata_lookup, doc_id, ["source"]),
                    "file_path": first_available({}, metadata_lookup, doc_id, ["file_path", "path"]),
                    "method": method,
                    "explanation": "Offline baseline result from latest 138-doc snapshot.",
                    "offline_note": "Offline baseline result from latest 138-doc snapshot.",
                }
            )
        detected = {"offline_baseline": [{"canonical": str(matched.iloc[0].get("query_text", query)), "label": method}]}
        return detected, rows, f"OFFLINE_BASELINE:{path}"
    return (
        {},
        [],
        "No matching offline baseline query found. Please use one of the core/extended query texts or run Hybrid/Vector realtime.",
    )


def run_retrieval_method(
    method: str,
    query: str,
    model,
    index,
    records: list[dict],
    metadata_lookup: dict[str, dict],
    term_index: list[dict],
    top_k: int,
) -> tuple[dict, list[dict], str]:
    if method == "Hybrid":
        with temporary_top_k(int(top_k)):
            detected, results = hybrid_search.hybrid_search(
                query=query,
                model=model,
                index=index,
                records=records,
                metadata_lookup=metadata_lookup,
                term_index=term_index,
            )
        return detected, results, "PASS"
    if method == "Vector":
        detected = hybrid_search.detect_entities(query, term_index)
        hits = hybrid_search.vector_only_search(
            query, model, index, records, top_k=max(int(top_k) * 10, int(top_k))
        )
        return detected, aggregate_vector_hits_to_docs(hits, metadata_lookup, int(top_k)), "PASS"
    if method == "Vector + metadata":
        detected, results = vector_metadata_search(
            query, model, index, records, metadata_lookup, term_index, int(top_k)
        )
        return detected, results, "PASS"
    if method in OFFLINE_FALLBACK_METHODS:
        return offline_baseline_results(method, query, metadata_lookup, int(top_k))
    return (
        {},
        [],
        f"{method} is documented in the UI but is not enabled for realtime Streamlit search in this safe UI pass.",
    )


def make_export_dataframe(
    query: str,
    method: str,
    results: list[Any],
    metadata_lookup: dict[str, dict],
    detected: Any,
) -> pd.DataFrame:
    rows = []
    detected_text = str(detected if detected else {})
    for rank, item in enumerate(results, start=1):
        doc_id = str(safe_get(item, "doc_id", default=""))
        rows.append(
            {
                "query": query,
                "method": method,
                "rank": rank,
                "doc_id": doc_id,
                "title": first_available(item, metadata_lookup, doc_id, ["title"]),
                "source": first_available(item, metadata_lookup, doc_id, ["source"]),
                "file_path": first_available(item, metadata_lookup, doc_id, ["file_path", "path"]),
                "final_score": safe_get(item, ["final_score", "score"], default=""),
                "vector_score": safe_get(item, ["vector_score", "score"], default=""),
                "metadata_delta": safe_get(item, ["metadata_delta", "kg_bonus"], default=""),
                "kg_score": safe_get(item, "kg_score", default=""),
                "intent_adjustment": safe_get(item, "intent_adjustment", default=""),
                "detected_entities": detected_text,
                "explanation": safe_get(item, ["explanation", "kg_explanation"], default=""),
                "kg_evidence_summary": kg_evidence_summary(item, metadata_lookup, detected),
            }
        )
    return pd.DataFrame(rows)


def excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="results")
    return buffer.getvalue()


def render_export_results(
    query: str,
    method: str,
    results: list[Any],
    metadata_lookup: dict[str, dict],
    detected: Any,
) -> None:
    st.subheader("Export results")
    if not results:
        st.info("No current results to export.")
        return
    df_export = make_export_dataframe(query, method, results, metadata_lookup, detected)
    safe_method = method.lower().replace(" + ", "_").replace("/", "_").replace(" ", "_")
    st.download_button(
        label="Download current results as Excel",
        data=excel_bytes(df_export),
        file_name=f"aquaculture_search_results_{safe_method}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


def render_method_comparison(
    query: str,
    top_k: int,
    model,
    index,
    records: list[dict],
    metadata_lookup: dict[str, dict],
    term_index: list[dict],
    current_method: str,
    current_results: list[Any],
) -> None:
    st.subheader("Compare retrieval methods")
    st.caption("Realtime comparison uses only methods with safe runtime functions. Offline baseline CSVs are not used to fake realtime results.")
    if not current_results:
        st.info("Run a search first to compare retrieval methods.")
        return
    method_to_view = st.selectbox(
        "Select method to view results",
        METHOD_OPTIONS,
        index=METHOD_OPTIONS.index(current_method) if current_method in METHOD_OPTIONS else 0,
        key="comparison_method",
    )
    if method_to_view == "Hybrid":
        comparison_results = current_results
        status = "PASS"
    elif method_to_view in ACTIVE_METHODS:
        with st.spinner(f"Running {method_to_view} comparison..."):
            _, comparison_results, status = run_retrieval_method(
                method_to_view,
                query,
                model,
                index,
                records,
                metadata_lookup,
                term_index,
                int(top_k),
            )
    elif method_to_view in OFFLINE_FALLBACK_METHODS:
        with st.spinner(f"Loading {method_to_view} offline baseline fallback..."):
            _, comparison_results, status = run_retrieval_method(
                method_to_view,
                query,
                model,
                index,
                records,
                metadata_lookup,
                term_index,
                int(top_k),
            )
        if status.startswith("OFFLINE_BASELINE"):
            st.info("Offline baseline result from latest 138-doc snapshot.")
        else:
            st.info(status)
            return
    else:
        st.info(f"{method_to_view} comparison is unavailable for the current query.")
        return
    if status != "PASS":
        st.info(status)
        return
    if not comparison_results:
        st.info(f"No {method_to_view} comparison results available. Run a search first or choose another method.")
        return
    rows = comparison_display_rows(comparison_results, metadata_lookup, method_to_view)
    render_comparison_table(rows, method_to_view)


def render_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
        }
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #f8fafc !important;
            color: #111827 !important;
        }
        .stApp {
            background: #f8fafc !important;
            color: #111827 !important;
        }
        [data-testid="stHeader"] {
            background: #ffffff !important;
            border-bottom: 1px solid #e5e7eb !important;
            color: #111827 !important;
        }
        [data-testid="stToolbar"] {
            background: #ffffff !important;
            color: #111827 !important;
        }
        [data-testid="stDecoration"] {
            background: #2563eb !important;
        }
        h1, h2, h3, h4, h5, h6, p, li, label, span, div, .stMarkdown {
            color: #111827 !important;
        }
        [data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid #d1d5db !important;
            color: #111827 !important;
            min-width: 22rem !important;
            width: 22rem !important;
        }
        [data-testid="stSidebar"] > div {
            background: #ffffff !important;
            color: #111827 !important;
            min-width: 22rem !important;
            width: 22rem !important;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {
            color: #111827 !important;
        }
        [data-testid="stSidebar"] small,
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] * {
            color: #374151 !important;
        }
        [data-testid="stTextInput"] input,
        [data-baseweb="input"],
        [data-baseweb="input"] input,
        input,
        textarea {
            background: #ffffff !important;
            color: #111827 !important;
            border-color: #cbd5e1 !important;
            caret-color: #111827 !important;
        }
        [data-testid="stTextInput"] input::placeholder,
        [data-baseweb="input"] input::placeholder,
        input::placeholder,
        textarea::placeholder {
            color: #6b7280 !important;
            opacity: 1 !important;
        }
        [data-baseweb="select"],
        [data-baseweb="select"] > div,
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {
            background: #ffffff !important;
            color: #111827 !important;
            border-color: #cbd5e1 !important;
        }
        [data-baseweb="select"] *,
        [data-baseweb="popover"] *,
        [data-baseweb="menu"] *,
        [role="option"] {
            color: #111827 !important;
        }
        [data-baseweb="select"] svg,
        [data-testid="stToolbar"] svg {
            color: #111827 !important;
            fill: #111827 !important;
        }
        .stButton button,
        button[kind="secondary"],
        [data-testid="stBaseButton-secondary"] {
            background: #eff6ff !important;
            color: #1d4ed8 !important;
            border: 1px solid #bfdbfe !important;
            border-radius: 8px !important;
            font-weight: 650 !important;
            min-height: 2.45rem !important;
            white-space: nowrap !important;
        }
        .stButton button:hover,
        button[kind="secondary"]:hover,
        [data-testid="stBaseButton-secondary"]:hover {
            background: #dbeafe !important;
            color: #1e40af !important;
            border-color: #93c5fd !important;
        }
        .stButton button:focus,
        .stButton button:active {
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18) !important;
        }
        button[kind="primary"],
        [data-testid="stBaseButton-primary"] {
            background: #2563eb !important;
            color: #ffffff !important;
            border: 1px solid #1d4ed8 !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
        }
        button[kind="primary"] *,
        [data-testid="stBaseButton-primary"] * {
            color: #ffffff !important;
        }
        button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {
            background: #1d4ed8 !important;
            color: #ffffff !important;
        }
        .header-panel {
            background: #ffffff !important;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 1rem;
        }
        .header-panel h1 {
            margin: 0 0 0.35rem 0;
            font-size: 2.05rem;
        }
        .header-panel p {
            margin: 0.2rem 0;
            font-size: 1rem;
            color: #374151 !important;
        }
        .runtime-note {
            font-size: 0.9rem;
            color: #4b5563 !important;
        }
        .section-note {
            color: #4b5563 !important;
            font-size: 0.92rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stExpander"] {
            background: #ffffff !important;
            border-color: #d1d5db !important;
            color: #111827 !important;
        }
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] div,
        [data-testid="stExpander"] p,
        [data-testid="stExpander"] span {
            background: #ffffff !important;
            color: #111827 !important;
        }
        .result-title {
            font-weight: 700;
            font-size: 1.05rem;
            margin-bottom: 0.75rem;
            color: #111827 !important;
        }
        .explanation {
            background: #f8fafc !important;
            border-left: 4px solid #2563eb;
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.98rem;
            line-height: 1.45;
            color: #111827 !important;
        }
        .snippet {
            background: #ffffff !important;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 0.75rem;
            color: #111827 !important;
            line-height: 1.45;
        }
        div[data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0.65rem;
        }
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #111827 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.35rem;
        }
        .stDataFrame,
        [data-testid="stDataFrame"],
        [data-testid="stDataFrame"] div,
        [data-testid="stDataFrame"] span,
        [data-testid="stTable"],
        [data-testid="stTable"] * {
            background: #ffffff !important;
            color: #111827 !important;
        }
        [data-testid="stDataFrame"] canvas {
            background: #ffffff !important;
        }
        .topk-table-wrap {
            width: 100%;
            overflow-x: auto;
            background: #ffffff !important;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            margin: 0.5rem 0 1rem 0;
        }
        .topk-table {
            width: 100%;
            border-collapse: collapse;
            background: #ffffff !important;
            color: #111827 !important;
            font-size: 0.92rem;
        }
        .topk-table thead tr {
            background: #f1f5f9 !important;
        }
        .topk-table th {
            color: #111827 !important;
            font-weight: 700;
            text-align: left;
            padding: 0.72rem 0.65rem;
            border-bottom: 1px solid #cbd5e1;
            white-space: nowrap;
        }
        .topk-table td {
            color: #111827 !important;
            background: #ffffff !important;
            padding: 0.65rem;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }
        .topk-table tbody tr:nth-child(even) td {
            background: #f8fafc !important;
        }
        .topk-table td.num {
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            text-align: right;
            white-space: nowrap;
            color: #1f2937 !important;
        }
        .topk-table td.text {
            color: #111827 !important;
            min-width: 7rem;
        }
        .topk-table td:nth-child(3) {
            min-width: 18rem;
        }
        .topk-table td:last-child {
            min-width: 12rem;
            color: #374151 !important;
        }
        pre,
        code,
        [data-testid="stJson"],
        [data-testid="stJson"] *,
        [data-testid="stCodeBlock"],
        [data-testid="stCodeBlock"] * {
            background: #f3f4f6 !important;
            color: #111827 !important;
            border-color: #d1d5db !important;
        }
        [data-testid="stAlert"],
        [data-testid="stAlert"] * {
            color: #111827 !important;
        }
        hr {
            border-color: #e5e7eb !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    render_global_style()

    with st.sidebar:
        st.header("Control panel")
        st.divider()
        st.subheader("Search controls")
        top_k = st.selectbox("Top-k", [3, 5, 10], index=1)
        method = st.selectbox("Method", METHOD_OPTIONS, index=0)
        if method in OFFLINE_FALLBACK_METHODS:
            st.caption(f"{method} uses offline baseline fallback when the query matches a saved core/extended query.")
        elif method not in ACTIVE_METHODS:
            st.caption(f"{method} is shown for comparison context; realtime search is not enabled for this method in the UI.")
        search_clicked = st.button("Search", type="primary", use_container_width=True)
        st.caption("Enter a query in the main panel, then click Search.")
        st.divider()
        st.subheader("Example queries")
        for example in EXAMPLE_QUERIES:
            if st.button(example, use_container_width=True):
                st.session_state["search_query"] = example
        st.divider()
        st.subheader("Optional post-result filters")
        st.caption("Filters only hide displayed results after retrieval; they do not change hybrid scoring.")
        disease_filter = st.text_input("Disease", "")
        species_filter = st.text_input("Species/Taxon", "")
        location_filter = st.text_input("Location", "")
        source_filter = st.text_input("Source", "")

    model, index, records, metadata_lookup, term_index = load_runtime_resources()

    st.markdown(
        """
        <div class="header-panel">
            <h1>Aquaculture Semantic Search Demo</h1>
            <p>Vector retrieval + metadata matching + ontology/KG evidence + hybrid reranking</p>
            <p class="runtime-note">This demo uses the existing runtime functions and does not modify retrieval scoring or evaluation metrics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Corpus", f"{len(metadata_lookup):,} documents")
    metric_cols[1].metric("Vector chunks", f"{len(records):,}")
    metric_cols[2].metric("KG docs", f"{len(metadata_lookup):,}")
    metric_cols[3].metric("Core evaluation", f"{SNAPSHOT_CORE_QUERIES} queries")

    st.subheader("1. Input query")

    query = st.text_input(
        "Search query",
        key="search_query",
        placeholder="e.g., AHPND shrimp disease",
        help="Search uses existing runtime functions; Hybrid keeps the current production scoring path.",
    )
    st.caption(f"Selected method: {method} | Top-k: {top_k}")
    main_search_clicked = st.button("Search query", type="primary")
    search_requested = search_clicked or main_search_clicked

    if search_requested and not query.strip():
        st.warning("Enter a search query first.")

    if search_requested and query.strip():
        with st.spinner(f"Running {method} search..."):
            detected, results, method_status = run_retrieval_method(
                method,
                query.strip(),
                model,
                index,
                records,
                metadata_lookup,
                term_index,
                int(top_k),
            )
        if method_status not in {"PASS"} and not str(method_status).startswith("OFFLINE_BASELINE"):
            st.warning(method_status)
            detected, results, _ = run_retrieval_method(
                "Hybrid",
                query.strip(),
                model,
                index,
                records,
                metadata_lookup,
                term_index,
                int(top_k),
            )
            method = "Hybrid"
        elif str(method_status).startswith("OFFLINE_BASELINE"):
            st.info("Offline baseline result from latest 138-doc snapshot.")
        st.session_state["last_search"] = {
            "query": query.strip(),
            "method": method,
            "top_k": int(top_k),
            "detected": detected,
            "results": results,
        }
        st.session_state["last_query"] = query.strip()
        st.session_state["last_method"] = method
        st.session_state["last_results"] = results
        st.session_state["last_detected"] = detected

    last_search = st.session_state.get("last_search")
    if not last_search:
        st.info("Enter a query and run Search to view detected entities, Top-k results, explanations, KG evidence, and export options.")
        return

    query_used = str(last_search.get("query", query))
    method_used = str(last_search.get("method", method))
    detected = last_search.get("detected", {})
    results = last_search.get("results", [])

    filters = {
        "disease": disease_filter,
        "species": species_filter,
        "location": location_filter,
        "source": source_filter,
    }
    displayed_results = apply_post_filters(results, metadata_lookup, filters)

    left_col, right_col = st.columns([1.15, 1.0])
    with left_col:
        st.subheader("2. Detected query entities")
        render_detected_entities(detected)

        st.subheader("3. Top-k results")
        if not displayed_results:
            st.warning("No results to display after optional filters.")
            return

        if len(displayed_results) < int(top_k):
            st.info(
                f"Showing {len(displayed_results)} result(s). The runtime candidate pool may return fewer documents than the selected Top-k."
            )

        st.markdown(
            '<p class="section-note">Click/select a result on the right to inspect explanation and KG evidence. Post-result filters only affect visibility.</p>',
            unsafe_allow_html=True,
        )
        render_topk_table(displayed_results, metadata_lookup)

        render_method_comparison(
            query_used,
            int(top_k),
            model,
            index,
            records,
            metadata_lookup,
            term_index,
            method_used,
            displayed_results,
        )

    with right_col:
        st.subheader("4. Result details")
        render_result_details(displayed_results, metadata_lookup, detected)
        render_export_results(query_used, method_used, displayed_results, metadata_lookup, detected)


if __name__ == "__main__":
    main()
