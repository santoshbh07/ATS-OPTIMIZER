import unittest

from app.services.matcher import (
    extract_job_requirements,
    extract_resume_skills,
    find_skills_in_text,
    match_resume_to_job,
)


class MatcherTests(unittest.TestCase):
    def test_find_skills_in_text_detects_aliases_without_matching_inside_words(self):
        found = find_skills_in_text("Built APIs with Python, JS, React, and Node.js.")

        self.assertIn("Python", found)
        self.assertIn("JavaScript", found)
        self.assertIn("React", found)
        self.assertIn("Node.js", found)
        self.assertNotIn("C", found)

    def test_extract_resume_skills_separates_explicit_and_inferred_skills(self):
        parsed_resume = {
            "skills": {"skills": ["Python, SQL"]},
            "projects": {"Dashboard": ["Built with React and FastAPI."]},
            "experience": [],
            "education": {},
        }

        result = extract_resume_skills(parsed_resume)

        self.assertEqual(result["explicit"], ["Python", "SQL"])
        self.assertEqual(result["inferred"], ["FastAPI", "React"])
        self.assertEqual(result["all"], ["FastAPI", "Python", "React", "SQL"])

    def test_extract_job_requirements_classifies_required_and_preferred_items(self):
        job_description = "\n".join(
            [
                "Required: Python and SQL",
                "Preferred: Docker",
                "Bachelor's degree required",
            ]
        )

        result = extract_job_requirements(job_description)

        self.assertEqual(result["skills"]["required"], ["Python", "SQL"])
        self.assertEqual(result["skills"]["preferred"], ["Docker"])
        self.assertIn("bachelor", result["qualifications"]["required"]["education"])

    def test_match_resume_to_job_reports_matched_and_missing_requirements(self):
        parsed_resume = {
            "skills": {"skills": ["Python", "SQL"]},
            "projects": {},
            "experience": [],
            "education": {"degree": ["Bachelor of Science"]},
        }
        job_description = "\n".join(
            [
                "Required: Python, SQL, and Docker",
                "Preferred: Bachelor's degree",
            ]
        )

        result = match_resume_to_job(parsed_resume, job_description)

        self.assertEqual(result["matched_skills"], ["Python", "SQL"])
        self.assertEqual(result["missing_required_skills"], ["Docker"])
        self.assertEqual(result["matched_qualifications"], ["bachelor"])


if __name__ == "__main__":
    unittest.main()
