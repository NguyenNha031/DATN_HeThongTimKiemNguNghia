from __future__ import annotations

from contextlib import contextmanager
from html import escape
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
        source = first_available(item, metadata_lookup, doc_id, SOURCE_KEYS)
        rows.append(
            {
                "rank": rank,
                "doc_id": safe_get(item, "doc_id"),
                "title": safe_get(item, "title"),
                "final_score": score_or_na(item, ["final_score", "score"]),
                "vector_score": score_or_na(item, ["vector_score", "score"]),
                "metadata_delta": score_or_na(item, ["metadata_delta", "kg_bonus"]),
                "kg_score": score_or_na(item, "kg_score"),
                "intent_adjustment": score_or_na(item, "intent_adjustment"),
                "source/file": truncate_text(source, max_chars=90) if source else "N/A",
            }
        )
    return rows


def render_topk_table(results: list[Any], metadata_lookup: dict[str, dict]) -> None:
    rows = result_table_rows(results, metadata_lookup)
    if not rows:
        st.info("No Top-k rows to display.")
        return

    columns = [
        "rank",
        "doc_id",
        "title",
        "final_score",
        "vector_score",
        "metadata_delta",
        "kg_score",
        "intent_adjustment",
        "source/file",
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


def render_detected_entities(detected: Any) -> None:
    st.subheader("Detected query entities")
    rows = entity_rows(detected)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No entities detected.")
    with st.expander("Raw entities"):
        st.json(detected if detected else {"entities": "N/A"}, expanded=False)


def source_evidence(item: Any, metadata_lookup: dict[str, dict]) -> tuple[str, str]:
    doc_id = str(safe_get(item, "doc_id", default=""))
    snippet = truncate_text(first_available(item, None, doc_id, SNIPPET_KEYS), max_chars=450)
    source = first_available(item, metadata_lookup, doc_id, SOURCE_KEYS)
    return snippet, str(source or "")


def render_score_boxes(item: Any) -> None:
    cols = st.columns(5)
    cols[0].metric("Final score", score_or_na(item, ["final_score", "score"]))
    cols[1].metric("Vector", score_or_na(item, ["vector_score", "score"]))
    cols[2].metric("Metadata", score_or_na(item, ["metadata_delta", "kg_bonus"]))
    cols[3].metric("KG", score_or_na(item, "kg_score"))
    cols[4].metric("Intent", score_or_na(item, "intent_adjustment"))


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

    st.markdown(
        """
        <div class="header-panel">
            <h1>Aquaculture Semantic Search Demo</h1>
            <p>Hybrid retrieval demo using vector search, metadata matching, KG evidence, and intent guardrails.</p>
            <p class="runtime-note">This demo uses the existing hybrid_search runtime and does not modify scoring or evaluation metrics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Search controls")
        st.divider()
        top_k = st.selectbox("Top-k", [3, 5, 10], index=1)
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

    query = st.text_input(
        "Search query",
        key="search_query",
        placeholder="e.g., AHPND shrimp disease",
        help="Search runs through the existing hybrid retrieval runtime.",
    )

    model, index, records, metadata_lookup, term_index = load_runtime_resources()

    if search_clicked and not query.strip():
        st.warning("Enter a search query first.")

    if search_clicked and query.strip():
        with st.spinner("Running hybrid search..."):
            with temporary_top_k(int(top_k)):
                detected, results = hybrid_search.hybrid_search(
                    query=query.strip(),
                    model=model,
                    index=index,
                    records=records,
                    metadata_lookup=metadata_lookup,
                    term_index=term_index,
                )

        filters = {
            "disease": disease_filter,
            "species": species_filter,
            "location": location_filter,
        }
        displayed_results = apply_post_filters(results, metadata_lookup, filters)

        render_detected_entities(detected)

        if not displayed_results:
            st.warning("No results to display after optional filters.")
            return

        if len(displayed_results) < int(top_k):
            st.info(
                f"Showing {len(displayed_results)} result(s). The runtime candidate pool may return fewer documents than the selected Top-k."
            )

        st.subheader("Top-k results")
        st.markdown(
            '<p class="section-note">Scores are displayed from the runtime result object; post-result filters only affect visibility.</p>',
            unsafe_allow_html=True,
        )
        render_topk_table(displayed_results, metadata_lookup)

        st.subheader("Result details")
        render_result_cards(displayed_results, metadata_lookup)


if __name__ == "__main__":
    main()
