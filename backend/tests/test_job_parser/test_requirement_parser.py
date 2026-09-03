from app.services.job_parsing.requirement_parser import parse_requirements


def test_parse_requirements_classifies_required_and_preferred_items():
    records = parse_requirements(
        {
            "requirements": [
                "- Bachelor's degree in Computer Science",
                "- 3+ years of backend experience",
                "- Strong communication skills",
            ],
            "preferred_requirements": ["AWS certification"],
            "skills": ["Python, SQL"],
        }
    )

    assert [(record.category, record.is_preferred) for record in records] == [
        ("education", False),
        ("experience", False),
        ("soft_skill", False),
        ("certification", True),
        ("skill", False),
        ("skill", False),
    ]
    assert [record.text for record in records[-2:]] == ["Python", "SQL"]


def test_required_duplicate_wins_over_preferred_duplicate():
    records = parse_requirements(
        {
            "preferred_requirements": ["Python"],
            "requirements": ["Python"],
        }
    )

    assert len(records) == 1
    assert records[0].is_preferred is False


def test_parse_requirements_uses_clear_overview_requirements_as_fallback():
    records = parse_requirements(
        {"job_overview": ["Applicants must know Python.", "We build APIs."]}
    )

    assert [record.text for record in records] == ["Applicants must know Python."]
