import unittest

from app.services.parser.parsers import (
    education_parser,
    experience_parser,
    has_bullet,
    normalize_text,
    skill_parser,
    strip_bullet,
)


class ParserHelperTests(unittest.TestCase):
    def test_normalize_text_repairs_common_mojibake_punctuation(self):
        apostrophe = "".join(map(chr, [0x00E2, 0x20AC, 0x2122]))
        smart_quote = "".join(map(chr, [0x00E2, 0x20AC, 0x0153]))

        self.assertEqual(normalize_text(f"Student{apostrophe}s resume"), "Student's resume")
        self.assertEqual(normalize_text(f"{smart_quote}Python"), '"Python')

    def test_strip_bullet_removes_supported_bullet_markers(self):
        bullet = chr(0x2022)

        self.assertEqual(strip_bullet(f"{bullet} Built an API"), "Built an API")

    def test_has_bullet_detects_supported_bullet_markers(self):
        bullet = chr(0x2022)

        self.assertTrue(has_bullet(f"{bullet} Built an API"))
        self.assertFalse(has_bullet("Built an API"))

    def test_skill_parser_removes_bullets_and_empty_lines(self):
        bullet = chr(0x2022)

        result = skill_parser([f"{bullet} Python", "", "  SQL  "])

        self.assertEqual(result, {"skills": ["Python", "SQL"]})

    def test_education_parser_groups_known_education_lines(self):
        result = education_parser(
            [
                "Bachelor of Science in Computer Science",
                "GPA: 3.8",
                "Relevant Coursework: Algorithms",
                "Database Systems",
            ]
        )

        self.assertEqual(result["degree"], ["Bachelor of Science in Computer Science"])
        self.assertEqual(result["gpa"], ["GPA: 3.8"])
        self.assertEqual(
            result["courseworks"],
            ["Relevant Coursework: Algorithms", "Database Systems"],
        )

    def test_experience_parser_builds_structured_entries(self):
        bullet = chr(0x2022)
        result = experience_parser(
            [
                "Acme Corp",
                "Software Engineer",
                "Jan 2024 - Present",
                f"{bullet} Built APIs with Python.",
            ]
        )

        self.assertEqual(
            result,
            [
                {
                    "company": "Acme Corp",
                    "position": "Software Engineer",
                    "date": "Jan 2024 - Present",
                    "description": [f"{bullet} Built APIs with Python."],
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
