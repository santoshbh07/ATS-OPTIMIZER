from pathlib import Path
from tempfile import NamedTemporaryFile
import logging
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.schemas.job import JobDescription, JobTextRequest
from app.schemas.resume import Resume
from app.services.job_parsing import parse_job_description
from app.services.resume_parsing.resume_parser import parse_resume_file

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ATS Optimizer API",
    version="0.1.0",
)

SUPPORTED_FILE_EXTENSIONS = {
    ".pdf",
    ".docx",
}


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "ATS Optimizer API is running",
    }


@app.post("/parse-resume", response_model=Resume)
def parse_resume_endpoint(
    file: UploadFile = File(...),
) -> dict[str, list[dict[str, object]]]:
    temporary_path: Path | None = None

    try:
        temporary_path = _save_uploaded_file(file)
        return parse_resume_file(temporary_path)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error while parsing resume")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while parsing the resume.",
        ) from exc

    finally:
        file.file.close()

        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


@app.post("/parse-job", response_model=JobDescription)
def parse_job_endpoint(request: JobTextRequest) -> dict[str, object]:
    try:
        return parse_job_description(request.text)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error while parsing job description")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while parsing the job description.",
        ) from exc


def _save_uploaded_file(file: UploadFile) -> Path:
    filename = file.filename or ""
    file_extension = Path(filename).suffix.lower()

    if file_extension not in SUPPORTED_FILE_EXTENSIONS:
        supported = ", ".join(
            sorted(SUPPORTED_FILE_EXTENSIONS)
        )

        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type: "
                f"{file_extension or 'unknown'}. "
                f"Supported types: {supported}."
            ),
        )

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
        ) as temporary_file:
            shutil.copyfileobj(
                file.file,
                temporary_file,
            )

            return Path(temporary_file.name)

    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="The uploaded file could not be saved.",
        ) from exc
