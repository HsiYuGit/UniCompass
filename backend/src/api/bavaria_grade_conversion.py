"""Bavaria grade and credit conversion helpers."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


DEFAULT_ECTS_PER_YEAR = 60


def convert_bavaria_grade(input_data: dict[str, Any]) -> dict[str, Any]:
    values = _normalize_input(input_data)
    target_ects_credits = _round(values["normalDurationYears"] * DEFAULT_ECTS_PER_YEAR, 2)
    conversion_factor_exact = _round(target_ects_credits / values["totalUniversityCredits"], 6)
    german_grade_exact = _round(
        1
        + (
            3
            * (values["highestPossibleGrade"] - values["currentOverallGrade"])
            / (values["highestPossibleGrade"] - values["lowestPassingGrade"])
        ),
        2,
    )

    return {
        "input": {
            "normalDurationYears": values["normalDurationYears"],
            "totalUniversityCredits": values["totalUniversityCredits"],
            "highestPossibleGrade": values["highestPossibleGrade"],
            "lowestPassingGrade": values["lowestPassingGrade"],
            "currentOverallGrade": values["currentOverallGrade"],
        },
        "creditConversion": {
            "ectsPerAcademicYear": DEFAULT_ECTS_PER_YEAR,
            "targetEctsCredits": target_ects_credits,
            "conversionFactorExact": conversion_factor_exact,
            "conversionFactorDisplay": _round(conversion_factor_exact, 2),
            "formula": "normalDurationYears * 60 / totalUniversityCredits",
        },
        "gradeConversion": {
            "germanGradeExact": german_grade_exact,
            "germanGradeDisplay": _truncate_to_decimal_places(german_grade_exact, 1),
            "formula": "1 + 3 * ((highestPossibleGrade - currentOverallGrade) / (highestPossibleGrade - lowestPassingGrade))",
        },
        "courses": [
            _convert_course(course, conversion_factor_exact)
            for course in values["courses"]
        ],
    }


def write_bavaria_grade_conversion_json(
    input_data: dict[str, Any], output_path: str | Path
) -> dict[str, Any]:
    if not output_path:
        raise ValueError("output_path must be a non-empty path")

    result = convert_bavaria_grade(input_data)
    path = Path(output_path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    return {
        "outputPath": str(path),
        "result": result,
    }


def _convert_course(course: dict[str, Any], conversion_factor_exact: float) -> dict[str, Any]:
    converted_credits_exact = _round(course["credits"] * conversion_factor_exact, 6)
    weighted_grade_points_exact = (
        None
        if course["grade"] is None
        else _round(converted_credits_exact * course["grade"], 6)
    )

    return {
        "module": course["module"],
        "originalCredits": course["credits"],
        "convertedCreditsExact": converted_credits_exact,
        "convertedCreditsDisplay": _round(converted_credits_exact, 2),
        "grade": course["grade"],
        "weightedGradePointsExact": weighted_grade_points_exact,
        "weightedGradePointsDisplay": None
        if weighted_grade_points_exact is None
        else _round(weighted_grade_points_exact, 2),
    }


def _normalize_input(input_data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")

    values = {
        "normalDurationYears": _number_from(
            input_data.get("normalDurationYears"), "normalDurationYears"
        ),
        "totalUniversityCredits": _number_from(
            input_data.get("totalUniversityCredits"), "totalUniversityCredits"
        ),
        "highestPossibleGrade": _number_from(
            input_data.get("highestPossibleGrade"), "highestPossibleGrade"
        ),
        "lowestPassingGrade": _number_from(
            input_data.get("lowestPassingGrade"), "lowestPassingGrade"
        ),
        "currentOverallGrade": _number_from(
            input_data.get("currentOverallGrade"), "currentOverallGrade"
        ),
        "courses": [
            _normalize_course(course, index)
            for index, course in enumerate(input_data.get("courses", []))
        ],
    }

    if values["normalDurationYears"] <= 0:
        raise ValueError("normalDurationYears must be greater than 0")

    if values["totalUniversityCredits"] <= 0:
        raise ValueError("totalUniversityCredits must be greater than 0")

    if values["highestPossibleGrade"] == values["lowestPassingGrade"]:
        raise ValueError("highestPossibleGrade and lowestPassingGrade cannot be equal")

    min_grade = min(values["highestPossibleGrade"], values["lowestPassingGrade"])
    max_grade = max(values["highestPossibleGrade"], values["lowestPassingGrade"])

    if not min_grade <= values["currentOverallGrade"] <= max_grade:
        raise ValueError(
            "currentOverallGrade must be between highestPossibleGrade and lowestPassingGrade"
        )

    return values


def _normalize_course(course: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(course, dict):
        raise TypeError(f"courses[{index}] must be a dictionary")

    credits = _number_from(course.get("credits"), f"courses[{index}].credits")

    if credits < 0:
        raise ValueError(f"courses[{index}].credits cannot be negative")

    return {
        "module": course.get("module") or course.get("name") or f"Course {index + 1}",
        "credits": credits,
        "grade": None
        if course.get("grade") is None
        else _number_from(course.get("grade"), f"courses[{index}].grade"),
    }


def _number_from(value: Any, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field_name} must be a finite number") from exc

    if not math.isfinite(parsed):
        raise TypeError(f"{field_name} must be a finite number")

    return int(parsed) if parsed.is_integer() else parsed


def _round(value: float, decimal_places: int) -> float:
    factor = 10**decimal_places
    adjusted = (value + sys_float_epsilon()) * factor
    if adjusted < 0:
        return math.ceil(adjusted - 0.5) / factor
    return math.floor(adjusted + 0.5) / factor


def _truncate_to_decimal_places(value: float, decimal_places: int) -> float:
    factor = 10**decimal_places
    return math.trunc(value * factor) / factor


def sys_float_epsilon() -> float:
    return 2.220446049250313e-16
