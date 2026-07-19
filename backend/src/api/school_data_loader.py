"""Parses data/schools/*.json fixtures into SchoolRequirements for recommand_agent.

Each file under data/schools/ is one school+program admission-requirements
record collected by the school data team. This module is the only place that
should read those raw files directly; everything downstream (recommand_agent)
works with the already-parsed SchoolRequirements dataclass.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parents[1]  # backend/src
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from models.recommand_agent import (  # noqa: E402
    CourseworkCredits,
    CreditGroup,
    LanguageRequirement,
    SchoolRequirements,
)

SCHOOLS_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "schools"


def _load_raw_records(data_dir: Path = SCHOOLS_DATA_DIR) -> list[dict]:
    records = []
    for path in sorted(data_dir.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            records.append(json.load(f))
    return records


def parse_school_requirements(raw: dict) -> SchoolRequirements:
    """Converts one raw fixture record into the agent's SchoolRequirements shape."""
    data = raw["data"]
    program = data["program"]
    entrance = data["entrance_requirements"]
    coursework = entrance["coursework_credits"]

    coursework_credits = CourseworkCredits(
        minimum_total=coursework["minimum_total"],
        groups=[
            CreditGroup(id=g["id"], minimum_credits=g["minimum_credits"], topics=g["topics"])
            for g in coursework.get("groups", [])
        ],
    )

    language_requirements = [
        LanguageRequirement(
            language=lr["language"],
            required=lr["required"],
            minimum_level=lr.get("minimum_level"),
            accepted_proofs=lr.get("accepted_proofs", []),
        )
        for lr in entrance.get("language_requirements", [])
    ]

    # SchoolRequirements.unmodeled_requirements is the free-text catch-all the
    # Step 3 agent already reads for judgement calls. Two bits of the raw
    # fixture don't have a dedicated field on that dataclass, so they are
    # folded in here as plain-text notes instead of being silently dropped:
    #   - entrance_requirements.academic_degree.field (e.g. "computer_science_or_related")
    #   - entrance_requirements.standardized_tests (e.g. GRE "strongly_recommended")
    unmodeled_requirements = list(entrance.get("unmodeled_requirements", []))
    degree = entrance.get("academic_degree", {})
    if degree.get("field"):
        unmodeled_requirements.append(f"Preferred undergraduate field: {degree['field']}")
    for test in entrance.get("standardized_tests", []):
        unmodeled_requirements.append(
            f"Standardized test note: {test.get('test_type')} ({test.get('requirement_level')})"
        )

    return SchoolRequirements(
        school=data["school"]["name"],
        program=program["name"],
        degree_level=program["degree_level"],
        coursework_credits=coursework_credits,
        language_requirements=language_requirements,
        unmodeled_requirements=unmodeled_requirements,
        verification_status=raw.get("collection_metadata", {}).get("verification_status", "unverified"),
    )


def load_school_requirements(data_dir: Path = SCHOOLS_DATA_DIR) -> list[SchoolRequirements]:
    """Reads every school fixture file and returns SchoolRequirements, ready for run_recommend_agent."""
    return [parse_school_requirements(raw) for raw in _load_raw_records(data_dir)]


def schools_to_json(schools: list[SchoolRequirements]) -> str:
    """Serializes parsed SchoolRequirements back to a JSON string."""
    return json.dumps([asdict(s) for s in schools], ensure_ascii=False, indent=2)


def save_school_requirements(schools: list[SchoolRequirements], output_path: Path) -> None:
    """Writes parsed SchoolRequirements to `output_path` as a single JSON array."""
    output_path.write_text(schools_to_json(schools), encoding="utf-8")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("schools_parsed.json")
    parsed = load_school_requirements()
    save_school_requirements(parsed, out)
    print(f"Wrote {len(parsed)} schools to {out}")
