import json
from pathlib import Path

import pytest

from src.models.recommand_agent import CourseClassification, CreditGroup, TranscriptSubject, _validate_classifications
from src.services.recommendation_service import (
    ProgrammeNotFoundError,
    agent_inputs_from_transcript,
    load_school_catalogue,
    select_programmes,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_transcript_adapter_converts_local_credits_to_ects():
    transcript = json.loads(
        (PROJECT_ROOT / "data" / "transcripts" / "computer_science_high_performance_high_related_experience.json").read_text(
            encoding="utf-8"
        )
    )

    grades, subjects, preferences = agent_inputs_from_transcript(transcript)

    assert grades.graduation_credits_completed == 192
    assert subjects[0] == TranscriptSubject("Academic Writing and Research Methods", 4.0)
    assert preferences.target_degree == "master"


def test_catalogue_selection_requires_known_programme():
    catalogue = load_school_catalogue(PROJECT_ROOT / "data")
    school = catalogue[0]

    assert select_programmes(catalogue, [{"school": school.school, "program": school.program}]) == [school]

    with pytest.raises(ProgrammeNotFoundError):
        select_programmes(catalogue, [{"school": "missing", "program": "missing"}])


def test_course_validation_rejects_credit_changes():
    subjects = [TranscriptSubject("Calculus", 3)]
    groups = [CreditGroup("mathematics", 3, ["calculus"])]

    with pytest.raises(ValueError, match="changed the credits"):
        _validate_classifications(
            [CourseClassification("Calculus", 4, "mathematics")], subjects, groups
        )
