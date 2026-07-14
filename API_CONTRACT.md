# ATS Optimizer API Contract

## Status

This contract is provisional.

The initial frontend will use mock data with this structure. The contract should
be reviewed against the existing Python backend before real API integration.

Database persistence is not part of the initial integration.

## Analyze Resume

### Intended Endpoint

POST /api/analyze

The final path may change after inspecting the existing FastAPI routes.

### Request Type

multipart/form-data

### Request Fields

#### resume

- Type: File
- Required: Yes
- Initially supported formats:
  - PDF
  - DOCX

#### job_description

- Type: String
- Required: Yes
- Must contain meaningful job-description content

## Example Success Response

```json
{
  "analysis_id": null,
  "file_name": "resume.pdf",
  "overall_score": 78,
  "keyword_score": 72,
  "formatting_score": 86,
  "matched_keywords": [
    "Python",
    "FastAPI",
    "JavaScript"
  ],
  "missing_keywords": [
    "Docker",
    "PostgreSQL"
  ],
  "detected_skills": [
    "Python",
    "HTML",
    "CSS",
    "JavaScript"
  ],
  "section_feedback": [
    {
      "section": "experience",
      "score": 75,
      "message": "The experience section contains relevant work but could use more measurable results."
    }
  ],
  "recommendations": [
    {
      "category": "keywords",
      "severity": "high",
      "title": "Review missing technical keywords",
      "explanation": "The job description mentions Docker and PostgreSQL.",
      "suggestion": "Add these technologies only if they accurately represent your experience."
    }
  ]
}