from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import kg_runtime


Decision = Literal["ADD_NEW_ENTITY", "ADD_EXACT_ALIAS", "RECLASSIFY_PROPERTY", "DENY_AUTO_BACKFILL"]


@dataclass(frozen=True)
class NormalizationDecision:
    token: str
    source_field: str  # metadata column name
    candidate_property: str  # owl predicate local name (aboutTaxon/aboutDisease/...)
    normalized_label: str
    candidate_class: str | None
    candidate_property_suggested: str | None
    target_uri: str | None
    decision: Decision
    reason: str
    confidence: Literal["high", "medium", "low"]


def normalize_token(token: Any) -> str:
    return kg_runtime.normalize_kg_text(token)


def _lookup_exact_entity(
    kg_index: dict[str, Any],
    token_norm: str,
    expected_entity_type: str,
) -> tuple[str | None, str | None]:
    """
    Return (uri, label) if an exact alias exists for expected_entity_type.
    """
    l2e = kg_index.get("label_to_entities") or {}
    ents = l2e.get(token_norm) or []
    for e in ents:
        if (e.get("entity_type") or "") == expected_entity_type and e.get("uri"):
            return str(e["uri"]), str(e.get("label") or "")
    return None, None


def decide_token_action(
    token: str,
    source_field: str,
    candidate_property: str,
    kg_index: dict[str, Any],
    expected_entity_type: str,
) -> NormalizationDecision:
    """
    Conservative, property-aware decisioning layer.

    Principles:
    - Never coerce management/prevention/pathogen/topic into aboutDisease.
    - Never map generic taxon tokens to specific species.
    - Allow adding *generic* entities only when the ontology already has a matching class (Fish/Shrimp/Crustacean/ProductionMode).
    """
    raw = str(token or "").strip()
    n = normalize_token(raw)
    if not n:
        return NormalizationDecision(
            token=raw,
            source_field=source_field,
            candidate_property=candidate_property,
            normalized_label="",
            candidate_class=None,
            candidate_property_suggested=None,
            target_uri=None,
            decision="DENY_AUTO_BACKFILL",
            reason="empty token",
            confidence="low",
        )

    # 1) Exact match already exists for the expected type.
    uri, _label = _lookup_exact_entity(kg_index, n, expected_entity_type)
    if uri:
        return NormalizationDecision(
            token=raw,
            source_field=source_field,
            candidate_property=candidate_property,
            normalized_label=n,
            candidate_class=None,
            candidate_property_suggested=candidate_property,
            target_uri=uri,
            decision="ADD_EXACT_ALIAS",
            reason="exact ontology alias match for expected entity type",
            confidence="high",
        )

    # 2) Property-aware DENY / RECLASSIFY for aboutDisease.
    if candidate_property == "aboutDisease":
        # Management / prevention / broad topics should not be asserted as Disease facts.
        deny_topics = {
            "health management",
            "disease risk",
            "disease control",
            "disease prevention",
            "aquatic animal diseases",
            "animal diseases",
            "fish diseases",
            "environmental impact",
            "pathogens",
            "pathogen introduction",
            "viroses",
            "viral disease",
            "biosecurity",
        }
        if n in deny_topics:
            # If ontology has a Prevention node for biosecurity, suggest reclassify (but do not backfill core facts).
            if n == "biosecurity":
                prev_uri, _ = _lookup_exact_entity(kg_index, n, "prevention")
                if prev_uri:
                    return NormalizationDecision(
                        token=raw,
                        source_field=source_field,
                        candidate_property=candidate_property,
                        normalized_label=n,
                        candidate_class="Prevention",
                        candidate_property_suggested="recommendedPrevention",
                        target_uri=prev_uri,
                        decision="RECLASSIFY_PROPERTY",
                        reason="biosecurity is Prevention (not Disease); do not assert aboutDisease",
                        confidence="high",
                    )
            return NormalizationDecision(
                token=raw,
                source_field=source_field,
                candidate_property=candidate_property,
                normalized_label=n,
                candidate_class=None,
                candidate_property_suggested=None,
                target_uri=None,
                decision="DENY_AUTO_BACKFILL",
                reason="topic/management/prevention/pathogen term; not a Disease fact",
                confidence="high",
            )

    # 3) Generic-but-valid Taxon entities (ONLY generic, never specific).
    # We allow creating generic individuals of existing ontology classes.
    if candidate_property == "aboutTaxon":
        # Token -> class local name (in this ontology)
        generic_taxon_class = {
            "fish": "Fish",
            "shrimp": "Shrimp",
            "crustaceans": "Crustacean",
            "crustacean": "Crustacean",
            "shellfish": "Taxon",
            "aquatic animals": "Taxon",
            "aquatic species": "Taxon",
        }.get(n)

        if generic_taxon_class:
            # Create a deterministic URI fragment under ontology namespace for generic nodes.
            ns = "http://www.semanticweb.org/lenovo/ontologies/2026/0/untitled-ontology-3#"
            frag = f"Generic_{generic_taxon_class}"
            # Keep multiple generic nodes distinct if needed.
            if n in {"shellfish", "aquatic animals", "aquatic species"}:
                frag = "Generic_AquaticTaxon"
            target_uri = ns + frag
            return NormalizationDecision(
                token=raw,
                source_field=source_field,
                candidate_property=candidate_property,
                normalized_label=n,
                candidate_class=generic_taxon_class,
                candidate_property_suggested=candidate_property,
                target_uri=target_uri,
                decision="ADD_NEW_ENTITY",
                reason="generic taxon term; safe to represent as generic Taxon individual",
                confidence="high",
            )

    # 4) Production modes: safe to add as ProductionMode individuals.
    if candidate_property == "documentProductionMode":
        mode_map = {
            "capture fisheries": ("ProductionMode", "Generic_CaptureFisheries"),
            "inland fisheries": ("ProductionMode", "Generic_InlandFisheries"),
            "coastal aquaculture": ("ProductionMode", "Generic_CoastalAquaculture"),
        }
        if n in mode_map:
            cls, frag = mode_map[n]
            ns = "http://www.semanticweb.org/lenovo/ontologies/2026/0/untitled-ontology-3#"
            return NormalizationDecision(
                token=raw,
                source_field=source_field,
                candidate_property=candidate_property,
                normalized_label=n,
                candidate_class=cls,
                candidate_property_suggested=candidate_property,
                target_uri=ns + frag,
                decision="ADD_NEW_ENTITY",
                reason="production mode term; safe to represent as ProductionMode individual",
                confidence="high",
            )

    # Default: deny auto backfill.
    return NormalizationDecision(
        token=raw,
        source_field=source_field,
        candidate_property=candidate_property,
        normalized_label=n,
        candidate_class=None,
        candidate_property_suggested=None,
        target_uri=None,
        decision="DENY_AUTO_BACKFILL",
        reason="no exact mapping; not safe to auto-create or assert",
        confidence="low",
    )

