# ATS Optimizer API Contract

## Status

This contract reflects the current FastAPI backend behavior.

The initial frontend may still use mock data, but mock data should be shaped to
match this contract so the later API integration is easier to understand and
maintain.

Database persistence is not part of the initial integration.

## Match Resume

### Endpoint

```text
POST /match-resume
```

### Request Type

```text
multipart/form-data
```

### Request Fields

#### file

- Type: File
- Required: Yes
- Currently supported by the parser:
  - PDF
  - DOCX

#### job_description

- Type: String
- Required: Yes
- Should contain meaningful job-description content.

## Response Shape

The endpoint returns three top-level objects:

```json
{
  "parsed_resume": {},
  "match_result": {},
  "score_result": {}
}
```

Returning each layer separately keeps the parser, matcher, and scorer outputs
visible to the frontend and easy to test.

## parsed_resume

`parsed_resume` is returned by `parse_resume()`.

```json
{
  "education": {
    "degree": ["Bachelor of Science in Computer Science"],
    "institution": ["State University"],
    "graduation": ["Expected Graduation: May 2027"],
    "gpa": ["GPA: 3.7"],
    "honors": ["Dean's List"],
    "minor": ["Minor in Mathematics"],
    "courseworks": ["Data Structures, Databases, Web Development"],
    "certifications": ["Microsoft Excel Certification"],
    "other": ["Additional education line"]
  },
  "skills": {
    "skills": ["Python, JavaScript, SQL, HTML, CSS, Git"]
  },
  "projects": {
    "Portfolio API": [
      "Built REST API with FastAPI and PostgreSQL.",
      "Used Docker for local development."
    ]
  },
  "experience": [
    {
      "company": "Campus Technology Services",
      "position": "Software Developer Intern",
      "date": "June 2025 - August 2025",
      "description": [
        "Built internal tools with Python and SQL.",
        "Collaborated with team using Git and GitHub."
      ]
    }
  ]
}
```

### parsed_resume Notes

- `education` category keys appear only when detected.
- `projects` is an object keyed by project title.
- `experience` is an array of parsed work entries.
- `experience.company`, `experience.position`, and `experience.date` may be
  empty strings when the parser cannot identify those values.
- `description` is an array of text lines.

## match_result

`match_result` is returned by `match_resume_to_job()`.

```json
{
  "resume_skills": {
    "explicit": ["CSS", "Git", "HTML", "JavaScript", "Python", "SQL"],
    "inferred": ["Docker", "FastAPI", "GitHub", "PostgreSQL", "React"],
    "all": [
      "CSS",
      "Docker",
      "FastAPI",
      "Git",
      "GitHub",
      "HTML",
      "JavaScript",
      "PostgreSQL",
      "Python",
      "React",
      "SQL"
    ]
  },
  "resume_qualifications": {
    "education": ["Bachelor of Science in Computer Science", "bachelor", "computer science"]
  },
  "job_requirements": {
    "skills": {
      "required": ["Docker", "FastAPI", "Python", "SQL"],
      "preferred": ["AWS", "PostgreSQL", "React"],
      "mentioned": []
    },
    "qualifications": {
      "required": {
        "education": ["bachelor"]
      },
      "preferred": {},
      "mentioned": {}
    }
  },
  "matched_skills": ["Docker", "FastAPI", "PostgreSQL", "Python", "React", "SQL"],
  "target_skills": ["AWS", "Docker", "FastAPI", "PostgreSQL", "Python", "React", "SQL"],
  "missing_required_skills": [],
  "missing_preferred_skills": ["AWS"],
  "matched_qualifications": ["bachelor"],
  "target_qualifications": ["bachelor"],
  "missing_required_qualifications": [],
  "missing_preferred_qualifications": []
}
```

### match_result Notes

- `resume_skills.explicit` contains skills found in the parsed skills section.
- `resume_skills.inferred` contains skills found in projects or experience.
- `resume_skills.all` combines explicit and inferred skills.
- `target_skills` combines required, preferred, and mentioned job skills.
- Missing skill fields are currently split into required and preferred only.
- Qualification category keys may be omitted when no values are detected.

## score_result

`score_result` is returned by `score_match()`.

```json
{
  "overall_score": 91,
  "skill_match_score": 86,
  "qualification_match_score": 100,
  "weights": {
    "skills": 0.65,
    "qualifications": 0.35
  }
}
```

### score_result Notes

- `overall_score` is the weighted combination of skill and qualification scores.
- `skill_match_score` compares `matched_skills` with `target_skills`.
- `qualification_match_score` compares `matched_qualifications` with
  `target_qualifications`.
- If there are no target skills or qualifications, that category currently
  scores `100`.

## Complete Example Success Response

```json
{
  "parsed_resume": {
    "education": {
      "degree": ["Bachelor of Science in Computer Science"],
      "institution": ["State University"],
      "graduation": ["Expected Graduation: May 2027"],
      "gpa": ["GPA: 3.7"],
      "courseworks": ["Data Structures, Databases, Web Development"]
    },
    "skills": {
      "skills": ["Python, JavaScript, SQL, HTML, CSS, Git"]
    },
    "projects": {
      "Portfolio API": [
        "Built REST API with FastAPI and PostgreSQL.",
        "Used Docker for local development."
      ],
      "Data Dashboard": [
        "Created React dashboard with Pandas analysis."
      ]
    },
    "experience": [
      {
        "company": "Campus Technology Services",
        "position": "Software Developer Intern",
        "date": "June 2025 - August 2025",
        "description": [
          "Built internal tools with Python and SQL.",
          "Collaborated with team using Git and GitHub."
        ]
      }
    ]
  },
  "match_result": {
    "resume_skills": {
      "explicit": ["CSS", "Git", "HTML", "JavaScript", "Python", "SQL"],
      "inferred": ["Docker", "FastAPI", "GitHub", "Pandas", "PostgreSQL", "React"],
      "all": [
        "CSS",
        "Docker",
        "FastAPI",
        "Git",
        "GitHub",
        "HTML",
        "JavaScript",
        "Pandas",
        "PostgreSQL",
        "Python",
        "React",
        "SQL"
      ]
    },
    "resume_qualifications": {
      "education": ["Bachelor of Science in Computer Science", "bachelor", "computer science"]
    },
    "job_requirements": {
      "skills": {
        "required": ["Docker", "FastAPI", "Python", "SQL"],
        "preferred": ["AWS", "PostgreSQL", "React"],
        "mentioned": []
      },
      "qualifications": {
        "required": {
          "education": ["bachelor"]
        },
        "preferred": {},
        "mentioned": {}
      }
    },
    "matched_skills": ["Docker", "FastAPI", "PostgreSQL", "Python", "React", "SQL"],
    "target_skills": ["AWS", "Docker", "FastAPI", "PostgreSQL", "Python", "React", "SQL"],
    "missing_required_skills": [],
    "missing_preferred_skills": ["AWS"],
    "matched_qualifications": ["bachelor"],
    "target_qualifications": ["bachelor"],
    "missing_required_qualifications": [],
    "missing_preferred_qualifications": []
  },
  "score_result": {
    "overall_score": 91,
    "skill_match_score": 86,
    "qualification_match_score": 100,
    "weights": {
      "skills": 0.65,
      "qualifications": 0.35
    }
  }
}
```

## Recommended First Frontend Fields

The first frontend should focus on fields the backend currently returns:

- `score_result.overall_score`
- `score_result.skill_match_score`
- `score_result.qualification_match_score`
- `match_result.matched_skills`
- `match_result.missing_required_skills`
- `match_result.missing_preferred_skills`
- `match_result.resume_skills.explicit`
- `match_result.resume_skills.inferred`
- `match_result.matched_qualifications`
- `match_result.missing_required_qualifications`
- `match_result.missing_preferred_qualifications`

## Fields Not Currently Returned

The backend does not currently return these planned or mock-only fields:

- `analysis_id`
- `file_name`
- `keyword_score`
- `formatting_score`
- `matched_keywords`
- `missing_keywords`
- `detected_skills`
- `section_feedback`
- `recommendations`

If the frontend displays any of these before backend support exists, they should
come from mock data only and should not be treated as real API fields.

## Error Notes

- Unsupported file extensions currently raise a backend error from the parser.
- Frontend file validation is only for user experience.
- The backend should later add its own polished validation and error responses.
- Do not treat frontend validation as production security.
