def score_overlap(matched_items, target_items):
    if not target_items:
        return 100
    return round((len(matched_items) / len(target_items)) * 100)


def score_match(match_result, skill_weight=0.65, qualification_weight=0.35):
    matched_skills = set(match_result.get("matched_skills", []))
    target_skills = set(match_result.get("target_skills", []))

    matched_qualifications = set(match_result.get("matched_qualifications", []))
    target_qualifications = set(match_result.get("target_qualifications", []))

    skill_score = score_overlap(matched_skills, target_skills)
    qualification_score = score_overlap(matched_qualifications, target_qualifications)

    # Keep weights configurable so v1 can tune scoring without touching matcher logic.
    overall_score = round(
        (skill_score * skill_weight) +
        (qualification_score * qualification_weight)
    )

    return {
        "overall_score": overall_score,
        "skill_match_score": skill_score,
        "qualification_match_score": qualification_score,
        "weights": {
            "skills": skill_weight,
            "qualifications": qualification_weight,
        },
    }
