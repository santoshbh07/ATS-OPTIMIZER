import unittest

from app.services.scorer import score_match, score_overlap


class ScorerTests(unittest.TestCase):
    def test_score_overlap_returns_full_score_when_there_are_no_targets(self):
        self.assertEqual(score_overlap([], []), 100)

    def test_score_overlap_calculates_percentage_of_matched_targets(self):
        self.assertEqual(score_overlap(["Python", "FastAPI"], ["Python", "FastAPI", "SQL"]), 67)

    def test_score_match_combines_skill_and_qualification_scores_with_default_weights(self):
        match_result = {
            "matched_skills": ["Python", "FastAPI"],
            "target_skills": ["Python", "FastAPI", "SQL", "Docker"],
            "matched_qualifications": ["bachelor"],
            "target_qualifications": ["bachelor"],
        }

        result = score_match(match_result)

        self.assertEqual(result["skill_match_score"], 50)
        self.assertEqual(result["qualification_match_score"], 100)
        self.assertEqual(result["overall_score"], 68)
        self.assertEqual(result["weights"], {"skills": 0.65, "qualifications": 0.35})


if __name__ == "__main__":
    unittest.main()
