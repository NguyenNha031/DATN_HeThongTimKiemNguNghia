from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rdflib import Graph


ONTOLOGY_FILE = Path("data") / "ontology" / "taxon_enriched_facts_v2.owl"
OUTPUT_JSON = Path("outputs") / "ontology_reasoner_consistency_check.json"
OUTPUT_MD = Path("outputs") / "ontology_reasoner_consistency_check.md"

NOT_COMPLETED_NOTE = (
    "Reasoner-based consistency check was not completed; do not interpret this as proof of consistency."
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def local_name(value: Any) -> str:
    text = str(value)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text:
        return text.rsplit("/", 1)[-1]
    return text


def run_command(args: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": " ".join(args),
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except Exception as exc:
        return {
            "command": " ".join(args),
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }


def get_python_environment() -> dict[str, Any]:
    pip_info = run_command([sys.executable, "-m", "pip", "--version"])
    pip_install_attempted = os.environ.get("ONTOLOGY_REASONER_PIP_INSTALL_ATTEMPTED", "").strip().lower()
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "pip_available": pip_info.get("returncode") == 0,
        "pip_version_output": pip_info.get("stdout") or pip_info.get("stderr"),
        "pip_install_attempted": pip_install_attempted in {"1", "true", "yes"},
        "owlready2_version": get_installed_package_version("owlready2"),
    }


def get_installed_package_version(package_name: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(package_name)
    except Exception:
        return None


def parse_ontology_with_rdflib(path: Path) -> dict[str, Any]:
    out = {
        "parse_ok": False,
        "triple_count": None,
        "error": None,
    }
    try:
        graph = Graph()
        graph.parse(str(path))
        out["parse_ok"] = True
        out["triple_count"] = len(graph)
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def find_external_reasoner_jars() -> list[str]:
    patterns = ["*hermit*.jar", "*pellet*.jar"]
    found: list[str] = []
    search_dirs = [Path("."), Path("tools"), Path("lib"), Path("reasoners"), Path("bin")]
    for pattern in patterns:
        for base in search_dirs:
            if not base.exists():
                continue
            for p in base.glob(pattern):
                if p.is_file():
                    found.append(str(p))
    return sorted(set(found))


def split_reasoner_jars(paths: list[str]) -> dict[str, Any]:
    hermit = [p for p in paths if "hermit" in Path(p).name.lower()]
    pellet = [p for p in paths if "pellet" in Path(p).name.lower()]
    return {
        "hermit_jar_found": bool(hermit),
        "hermit_jars": hermit,
        "pellet_jar_found": bool(pellet),
        "pellet_jars": pellet,
    }


def collect_unsatisfiable_classes(world: Any) -> list[str]:
    try:
        inconsistent_classes = list(world.inconsistent_classes())
    except Exception:
        inconsistent_classes = []
    out = []
    for cls in inconsistent_classes:
        name = getattr(cls, "iri", None) or getattr(cls, "name", None) or str(cls)
        if "Nothing" in str(name):
            continue
        out.append(str(name))
    return sorted(set(out))


def try_owlready2_reasoner(path: Path) -> dict[str, Any]:
    attempted: list[dict[str, Any]] = []
    if importlib.util.find_spec("owlready2") is None:
        return {
            "available": False,
            "completed": False,
            "reasoner_used": None,
            "is_consistent": None,
            "unsatisfiable_classes": [],
            "attempted_methods": [
                {
                    "method": "owlready2",
                    "status": "not_available",
                    "message": "Python package owlready2 is not installed.",
                }
            ],
            "error_message": "Python package owlready2 is not installed.",
        }

    try:
        from owlready2 import (  # type: ignore
            OwlReadyInconsistentOntologyError,
            World,
            get_ontology,
            sync_reasoner,
            sync_reasoner_pellet,
        )
    except Exception as exc:
        return {
            "available": False,
            "completed": False,
            "reasoner_used": None,
            "is_consistent": None,
            "unsatisfiable_classes": [],
            "attempted_methods": [
                {
                    "method": "owlready2_import",
                    "status": "failed",
                    "message": f"{type(exc).__name__}: {exc}",
                }
            ],
            "error_message": f"Failed to import owlready2 reasoner APIs: {type(exc).__name__}: {exc}",
        }

    try:
        world = World()
        # Owlready2 on Windows can fail on file:///C:/... URIs by rewriting them
        # to /C:/... paths. Passing the native absolute path is more reliable.
        onto = world.get_ontology(str(path.resolve())).load()
    except Exception as exc:
        return {
            "available": True,
            "completed": False,
            "reasoner_used": None,
            "is_consistent": None,
            "unsatisfiable_classes": [],
            "attempted_methods": [
                {
                    "method": "owlready2_load_ontology",
                    "status": "failed",
                    "message": f"{type(exc).__name__}: {exc}",
                }
            ],
            "error_message": f"owlready2 could not load ontology: {type(exc).__name__}: {exc}",
        }

    # Prefer Pellet because Owlready2 can report inconsistent classes after classification.
    for reasoner_name, runner in [
        ("owlready2_pellet", sync_reasoner_pellet),
        ("owlready2_hermit", sync_reasoner),
    ]:
        started = time.perf_counter()
        try:
            with onto:
                if reasoner_name == "owlready2_pellet":
                    runner([onto], infer_property_values=True, infer_data_property_values=True, debug=0)
                else:
                    runner([onto], debug=0)
            unsat = collect_unsatisfiable_classes(world)
            attempted.append(
                {
                    "method": reasoner_name,
                    "status": "completed",
                    "elapsed_seconds": round(time.perf_counter() - started, 4),
                    "message": "Reasoner completed.",
                }
            )
            return {
                "available": True,
                "completed": True,
                "reasoner_used": reasoner_name,
                "is_consistent": True,
                "unsatisfiable_classes": unsat,
                "attempted_methods": attempted,
                "error_message": None,
            }
        except OwlReadyInconsistentOntologyError as exc:
            unsat = collect_unsatisfiable_classes(world)
            attempted.append(
                {
                    "method": reasoner_name,
                    "status": "completed_inconsistent",
                    "elapsed_seconds": round(time.perf_counter() - started, 4),
                    "message": f"{type(exc).__name__}: {exc}",
                }
            )
            return {
                "available": True,
                "completed": True,
                "reasoner_used": reasoner_name,
                "is_consistent": False,
                "unsatisfiable_classes": unsat,
                "attempted_methods": attempted,
                "error_message": f"{type(exc).__name__}: {exc}",
            }
        except Exception as exc:
            attempted.append(
                {
                    "method": reasoner_name,
                    "status": "failed",
                    "elapsed_seconds": round(time.perf_counter() - started, 4),
                    "message": f"{type(exc).__name__}: {exc}",
                    "traceback_tail": traceback.format_exc().splitlines()[-6:],
                }
            )

    return {
        "available": True,
        "completed": False,
        "reasoner_used": None,
        "is_consistent": None,
        "unsatisfiable_classes": [],
        "attempted_methods": attempted,
        "error_message": "owlready2 was available, but both Pellet and HermiT runs failed.",
    }


def status_from_reasoner(reasoner_result: dict[str, Any]) -> str:
    if reasoner_result.get("completed"):
        return "completed"
    if reasoner_result.get("available") is False:
        return "not_available"
    return "failed"


def build_report() -> dict[str, Any]:
    started = time.perf_counter()
    python_env = get_python_environment()
    java_info = run_command(["java", "-version"])
    external_jars = find_external_reasoner_jars()
    jar_status = split_reasoner_jars(external_jars)
    parse_info = parse_ontology_with_rdflib(ONTOLOGY_FILE)
    reasoner_result = try_owlready2_reasoner(ONTOLOGY_FILE)

    attempted_methods = []
    attempted_methods.append(
        {
            "method": "java",
            "status": "available" if java_info.get("returncode") == 0 else "not_available",
            "message": java_info.get("stderr") or java_info.get("stdout") or "No Java output.",
        }
    )
    attempted_methods.append(
        {
            "method": "external_hermit_or_pellet_jar_search",
            "status": "found" if external_jars else "not_available",
            "message": external_jars if external_jars else "No HermiT/Pellet jar found in project root, tools/, lib/, reasoners/, or bin/.",
        }
    )
    attempted_methods.extend(reasoner_result.get("attempted_methods") or [])

    check_status = status_from_reasoner(reasoner_result)
    is_consistent = reasoner_result.get("is_consistent")
    unsat = reasoner_result.get("unsatisfiable_classes") or []
    unsat_count = len(unsat) if check_status == "completed" else None

    warnings_or_notes = [
        "This report is separate from the runtime-oriented ontology quality/coverage check.",
        "Runtime-oriented checks inspect structural statistics, document mapping, fact coverage, and dangling objects.",
        "Reasoner-based checks evaluate OWL logical consistency/class satisfiability when a reasoner can run.",
    ]
    if check_status in {"failed", "not_available"}:
        warnings_or_notes.append(NOT_COMPLETED_NOTE)
    if parse_info.get("parse_ok") and check_status in {"failed", "not_available"}:
        warnings_or_notes.append(
            "rdflib parsing succeeded, but RDF/XML parse success is not a reasoner-based consistency result."
        )

    if check_status == "completed" and is_consistent is True:
        conclusion = f"Ontology is consistent under {reasoner_result.get('reasoner_used')}."
        if not unsat:
            conclusion += " No unsatisfiable classes detected."
    elif check_status == "completed" and is_consistent is False:
        conclusion = f"Ontology is inconsistent under {reasoner_result.get('reasoner_used')}."
    else:
        conclusion = NOT_COMPLETED_NOTE

    return {
        "ontology_file": str(ONTOLOGY_FILE),
        "check_time": now_iso(),
        "elapsed_seconds": round(time.perf_counter() - started, 4),
        "check_status": check_status,
        "reasoner_used": reasoner_result.get("reasoner_used"),
        "is_consistent": is_consistent,
        "unsatisfiable_classes_count": unsat_count,
        "unsatisfiable_classes": unsat,
        "inferred_or_checked_summary": {
            "python_environment": python_env,
            "rdflib_parse": parse_info,
            "java_available": java_info.get("returncode") == 0,
            "external_reasoner_jars_found": external_jars,
            **jar_status,
            "owlready2_available": bool(importlib.util.find_spec("owlready2")),
        },
        "attempted_methods": attempted_methods,
        "error_message": reasoner_result.get("error_message"),
        "warnings_or_notes": warnings_or_notes,
        "limitations": [
            "No ontology, metadata, query set, relevance judgments, baseline outputs, or metric files are modified.",
            "If no reasoner completes, this report must not be used as proof of consistency.",
            "If a reasoner completes, the result is scoped to the loaded ontology file and the selected reasoner/tool behavior.",
            "This report does not replace runtime-oriented coverage checks or competency-question evaluation.",
        ],
        "conclusion": conclusion,
    }


def write_markdown(report: dict[str, Any]) -> None:
    status = report["check_status"]
    unsat = report.get("unsatisfiable_classes") or []
    summary = report.get("inferred_or_checked_summary") or {}
    python_env = summary.get("python_environment") or {}

    def compact_message(message: Any, max_len: int = 260) -> str:
        if isinstance(message, list):
            message = ", ".join(str(x) for x in message)
        text = str(message or "")
        text = " ".join(line.strip() for line in text.splitlines() if line.strip())
        if len(text) > max_len:
            return text[:max_len].rstrip() + " ... (full details in JSON)"
        return text

    lines = [
        "# Ontology Reasoner-based Consistency Check",
        "",
        "## Purpose",
        "",
        "This report checks the official runtime ontology with an OWL reasoner when the local environment supports it.",
        "It is distinct from the existing runtime-oriented quality check.",
        "",
        "## Ontology",
        "",
        f"- Ontology file: `{report['ontology_file']}`",
        f"- Check time: `{report['check_time']}`",
        f"- Python: `{python_env.get('python_version', '').split(' [', 1)[0]}`",
        f"- Owlready2: `{python_env.get('owlready2_version')}`",
        f"- pip install attempted in this task: `{python_env.get('pip_install_attempted')}`",
        "",
        "## Tooling Attempted",
        "",
    ]
    for item in report.get("attempted_methods", []):
        message = compact_message(item.get("message", ""))
        lines.append(f"- `{item.get('method')}`: {item.get('status')} - {message}")

    lines.extend(
        [
            "",
            "## Result",
            "",
            f"- Check status: `{status}`",
            f"- Reasoner used: `{report.get('reasoner_used')}`",
            f"- is_consistent: `{report.get('is_consistent')}`",
            f"- Unsatisfiable classes count: {report.get('unsatisfiable_classes_count')}",
        ]
    )
    if unsat:
        lines.append("- Unsatisfiable classes:")
        lines.extend(f"  - `{cls}`" for cls in unsat)
    elif status == "completed" and report.get("is_consistent") is True:
        lines.append("- No unsatisfiable classes detected.")
    else:
        lines.append("- Unsatisfiable classes were not determined because no reasoner completed.")

    if report.get("error_message"):
        lines.extend(["", "## Error", "", f"- {report['error_message']}"])

    lines.extend(["", "## Warnings and Notes", ""])
    lines.extend(f"- {note}" for note in report.get("warnings_or_notes", []))

    lines.extend(
        [
            "",
            "## Difference from Runtime-oriented Quality Check",
            "",
            "- The previous runtime-oriented quality check reports structural statistics, document mapping, fact coverage, dangling fact objects, duplicate local names, and label coverage.",
            "- This reasoner-based check attempts to evaluate OWL logical consistency and class satisfiability using a reasoner.",
            "- A successful structural/coverage check does not prove OWL consistency.",
            "- A failed or unavailable reasoner check must not be interpreted as proof that the ontology is consistent.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report.get("limitations", []))
    lines.extend(["", "## Conclusion", "", report["conclusion"], ""])

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not ONTOLOGY_FILE.exists():
        report = {
            "ontology_file": str(ONTOLOGY_FILE),
            "check_time": now_iso(),
            "elapsed_seconds": 0.0,
            "check_status": "failed",
            "reasoner_used": None,
            "is_consistent": None,
            "unsatisfiable_classes_count": 0,
            "unsatisfiable_classes": [],
            "inferred_or_checked_summary": {},
            "attempted_methods": [],
            "error_message": f"Ontology file not found: {ONTOLOGY_FILE}",
            "warnings_or_notes": [NOT_COMPLETED_NOTE],
            "limitations": ["Input ontology file is missing."],
            "conclusion": NOT_COMPLETED_NOTE,
        }
    else:
        report = build_report()

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)
    print(f"[OK] Wrote {OUTPUT_JSON} and {OUTPUT_MD}")
    print(f"[STATUS] {report['check_status']}; reasoner={report.get('reasoner_used')}; consistent={report.get('is_consistent')}")
    if report["check_status"] in {"failed", "not_available"}:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
