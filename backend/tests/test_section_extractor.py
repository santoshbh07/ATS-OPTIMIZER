import unittest

from app.services.parser.section_extractor import extract_sections, find_header_loc, is_header


class SectionExtractorTests(unittest.TestCase):
    def test_is_header_accepts_known_headers_with_punctuation(self):
        self.assertTrue(is_header("Technical Skills:"))
        self.assertTrue(is_header("Work Experience"))
        self.assertFalse(is_header("Built APIs with Python"))

    def test_find_header_loc_maps_resume_headers_to_sections(self):
        resume_text = "\n".join(
            [
                "Jane Candidate",
                "Technical Skills",
                "Python",
                "Education",
                "Bachelor of Science",
            ]
        )

        header_loc, positions = find_header_loc(resume_text)

        self.assertEqual(header_loc, {"skills": [1], "education": [3]})
        self.assertEqual(positions, [1, 3])

    def test_extract_sections_returns_content_between_headers(self):
        resume_text = "\n".join(
            [
                "Jane Candidate",
                "Skills",
                "Python",
                "SQL",
                "Projects",
                "ATS Optimizer",
            ]
        )
        header_loc, positions = find_header_loc(resume_text)

        result = extract_sections(resume_text, header_loc, positions)

        self.assertEqual(result["skills"], ["Python", "SQL"])
        self.assertEqual(result["projects"], ["ATS Optimizer"])


if __name__ == "__main__":
    unittest.main()
