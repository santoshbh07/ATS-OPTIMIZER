# ATS Optimizer

ATS Optimizer is a Python and FastAPI project for extracting structured data
from software-engineering resumes and job descriptions. Resume-to-job matching
and ATS-style scoring are the next planned development phase.

## Current Features

- PDF and DOCX resume uploads through FastAPI
- Resume text extraction with temporary-file cleanup
- Structured parsing for education, skills, projects, and experience
- Structured job-description parsing for metadata, requirements, and
  responsibilities
- Pydantic models that validate parser output
- Automated parser and schema tests

## Requirements

- Python 3.12
- Git

## Installation

From the repository root, create a virtual environment and install the pinned
dependencies:

```powershell
python -m venv backend/venv
.\backend\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source backend/venv/bin/activate
```

## Running the API

From the repository root:

```bash
python -m uvicorn app.main:app --app-dir backend --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is
available at `http://127.0.0.1:8000/docs`.

## Running Tests

```bash
python -m pytest backend/tests
```

## Project Structure

```text
ATS Optimizer/
├── backend/
│   ├── app/
│   │   ├── db/                       # Reserved for future persistence
│   │   ├── schemas/                  # Pydantic data contracts
│   │   ├── services/
│   │   │   ├── job_parsing/
│   │   │   ├── matching/             # Planned matching implementation
│   │   │   ├── resume_parsing/
│   │   │   └── resume_text_extractor/
│   │   └── main.py
│   ├── tests/
│   └── pytest.ini
├── .github/workflows/tests.yml
├── requirements.txt
└── README.md
```

## Roadmap

- Resume-to-job requirement matching
- Explainable category and overall scores
- Job-description API endpoint
- Vanilla HTML, CSS, and JavaScript frontend
- Database integration after the parsing and matching contracts stabilize

## Privacy

Do not commit real resumes, uploaded files, environment files, or personal data.
Local sample resumes and upload directories are excluded through `.gitignore`.

## License

This project is available under the [MIT License](LICENSE).
