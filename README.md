# ATS Optimizer

A Python-based ATS resume analysis project that compares a resume with a job description, extracts useful information, identifies keyword matches, and calculates ATS-style scores.

## Current Features

- Resume upload with FastAPI
- Resume text extraction and parsing
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
├── AGENTS.md
├── API_CONTRACT.md
├── FRONTEND_PLAN.md
└── README.md
```

## API Endpoints

```text
GET  /
POST /parse-resume
POST /match-resume
```

`POST /match-resume` accepts:

```text
file
job_description
```

and returns:

```json
{
  "parsed_resume": {},
  "match_result": {},
  "score_result": {}
}
```

## Run the Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Planned Frontend

The frontend will use:

- HTML
- CSS
- Vanilla JavaScript

It will be added in a separate root-level `frontend/` directory.

## Database

Database development is intentionally postponed. The `backend/app/db/` directory should remain unchanged until database implementation begins.

## Privacy

Do not commit real resumes, uploaded files, `.env` files, or personal data.

## Next Steps

- Build the frontend
- Connect it to `/match-resume`
- Improve backend validation and error handling
- Add database persistence later
