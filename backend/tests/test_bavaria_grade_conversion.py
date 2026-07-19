import json
import tempfile
import unittest
from pathlib import Path

from backend.src.api.bavaria_grade_conversion import (
    convert_bavaria_grade,
    write_bavaria_grade_conversion_json,
    write_default_bavaria_grade_conversion_json,
)


class BavariaGradeConversionTest(unittest.TestCase):
    def test_converts_gpa_screenshot_values(self):
        result = convert_bavaria_grade(
            {
                "normalDurationYears": 4,
                "totalUniversityCredits": 128,
                "highestPossibleGrade": 4,
                "lowestPassingGrade": 2,
                "currentOverallGrade": 3.88,
            }
        )

        self.assertEqual(result["gradeConversion"]["germanGradeExact"], 1.18)
        self.assertEqual(result["gradeConversion"]["germanGradeDisplay"], 1.1)

    def test_converts_credit_screenshot_values(self):
        result = convert_bavaria_grade(
            {
                "normalDurationYears": 4,
                "totalUniversityCredits": 128,
                "highestPossibleGrade": 4,
                "lowestPassingGrade": 2,
                "currentOverallGrade": 3.88,
                "courses": [
                    {
                        "module": "Applied Statistics",
                        "credits": 5,
                        "grade": 7,
                    }
                ],
            }
        )

        self.assertEqual(result["creditConversion"]["targetEctsCredits"], 240)
        self.assertEqual(result["creditConversion"]["conversionFactorExact"], 1.875)
        self.assertEqual(result["creditConversion"]["conversionFactorDisplay"], 1.88)
        self.assertEqual(result["courses"][0]["convertedCreditsDisplay"], 9.38)
        self.assertEqual(result["courses"][0]["weightedGradePointsDisplay"], 65.63)

    def test_writes_conversion_result_json(self):
        output_path = Path(tempfile.gettempdir()) / "python-bavaria-conversion.json"

        write_bavaria_grade_conversion_json(
            {
                "normalDurationYears": 4,
                "totalUniversityCredits": 128,
                "highestPossibleGrade": 4,
                "lowestPassingGrade": 2,
                "currentOverallGrade": 3.88,
            },
            output_path,
        )

        written = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(written["gradeConversion"]["germanGradeExact"], 1.18)
        self.assertEqual(written["creditConversion"]["conversionFactorDisplay"], 1.88)

    def test_writes_default_conversion_result_json_next_to_api_module(self):
        result = write_default_bavaria_grade_conversion_json(
            {
                "normalDurationYears": 4,
                "totalUniversityCredits": 128,
                "highestPossibleGrade": 4,
                "lowestPassingGrade": 2,
                "currentOverallGrade": 3.88,
                "courses": [
                    {
                        "module": "Applied Statistics",
                        "credits": 5,
                        "grade": 7,
                    }
                ],
            }
        )

        output_path = Path(result["outputPath"])
        written = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(output_path.name, "bavaria_conversion_result.json")
        self.assertEqual(output_path.parent.name, "api")
        self.assertEqual(written["creditConversion"]["conversionFactorDisplay"], 1.88)
        self.assertEqual(written["courses"][0]["weightedGradePointsDisplay"], 65.63)


if __name__ == "__main__":
    unittest.main()
