"""Adapters between persisted UniCompass fixtures and the recommendation agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.recommand_agent import (
    CourseworkCredits,
    CreditGroup,
    GradesCredits,
    LanguageCheck,
    LanguageRequirement,
    SchoolRequirements,
    StudentPreferences,
    TranscriptSubject,
)


class ProgrammeNotFoundError(ValueError):
    """The request referred to a programme not in the local catalogue."""


def default_data_root() -> Path:
    return Path(__file__).resolve().parents[3] / "data"


def school_requirements_from_record(record: dict[str, Any]) -> SchoolRequirements:
    data = record["data"]
    requirements = data["entrance_requirements"]
    coursework = requirements["coursework_credits"]
    return SchoolRequirements(
        school=data["school"]["name"],
        program=data["program"]["name"],
        degree_level=data["program"]["degree_level"],
        coursework_credits=CourseworkCredits(
            minimum_total=int(coursework["minimum_total"]),
            groups=[
                CreditGroup(
                    id=group["id"],
                    minimum_credits=int(group["minimum_credits"]),
                    topics=list(group["topics"]),
                )
                for group in coursework["groups"]
            ],
        ),
        language_requirements=[
            LanguageRequirement(
                language=requirement["language"],
                required=bool(requirement["required"]),
                minimum_level=requirement.get("minimum_level"),
                accepted_proofs=list(requirement.get("accepted_proofs", [])),
            )
            for requirement in requirements.get("language_requirements", [])
        ],
        unmodeled_requirements=list(requirements.get("unmodeled_requirements", [])),
        verification_status=record["collection_metadata"]["verification_status"],
    )


def load_school_catalogue(data_root: Path | None = None) -> list[SchoolRequirements]:
    root = data_root or default_data_root()
    schools: list[SchoolRequirements] = []
    for path in sorted((root / "schools").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") == "complete":
            schools.append(school_requirements_from_record(record))
    return schools


def select_programmes(
    catalogue: list[SchoolRequirements], selectors: list[dict[str, str]]
) -> list[SchoolRequirements]:
    selected: list[SchoolRequirements] = []
    seen: set[tuple[str, str]] = set()
    available = {(school.school, school.program): school for school in catalogue}
    for selector in selectors:
        key = (selector["school"], selector["program"])
        if key in seen:
            continue
        if key not in available:
            raise ProgrammeNotFoundError(
                f"Programme not found in catalogue: {selector['school']} / {selector['program']}"
            )
        seen.add(key)
        selected.append(available[key])
    return selected


def agent_inputs_from_transcript(
    transcript: dict[str, Any],
) -> tuple[GradesCredits, list[TranscriptSubject], StudentPreferences]:
    scores = transcript.get("language_scores", {})
    gre_details = scores.get("gre_details", {})
    grades = GradesCredits(
        gpa_normalized_4=float(transcript["gpa"]),
        is_graduated=bool(transcript["is_graduated"]),
        graduation_credits_completed=int(
            float(transcript["graduation_credits"]) * float(transcript.get("ects_multiplier", 1))
        ),
        language_check=LanguageCheck(
            german_level=transcript.get("german_level"),
            english_ielts=scores.get("ielts"),
            english_toefl=scores.get("toefl"),
            gre_verbal=gre_details.get("verbal"),
            gre_quant=gre_details.get("quant"),
            gre_writing=gre_details.get("writing"),
        ),
    )
    subjects = [
        TranscriptSubject(name=subject["name"], credits=float(subject["credits"]))
        for subject in transcript["transcript_subjects"]
    ]
    preferences = StudentPreferences(
        target_degree=transcript["target_degree"],
        experiences=list(transcript.get("experiences", [])),
        interests=list(transcript.get("interests", [])),
        preferred_countries=list(transcript.get("preferred_countries", [])),
        budget_usd_per_year=transcript.get("budget_usd_per_year"),
    )
    return grades, subjects, preferences
