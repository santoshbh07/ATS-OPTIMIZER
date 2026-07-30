# ATS Optimizer

A Python-based ATS resume analysis project that compares a resume with a job description, extracts useful information, identifies keyword matches, and calculates ATS-style scores, currently targeted for CS only resume.

## Planned Features 

### Currently working
- Resume upload with FastAPI
- Resume text extraction and parsing

### Will work on
- Resume-to-job-description matching 
- ATS scoring
- Temporary file cleanup
- API testing through FastAPI Docs

## Project Structure

```text
ATS OPTIMIZER/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   └── venv/
├── sample_resume/
├── tests/
└── README.md
```
## Planned Frontend

The frontend will use:

- HTML
- CSS
- Vanilla JavaScript

It will be added in a separate root-level `frontend/` directory.

## Database

Database development is intentionally postponed. The `backend/app/db/` directory remains unchanged until database implementation begins.

## Privacy

Do not commit real resumes, uploaded files, `.env` files, or personal data.
