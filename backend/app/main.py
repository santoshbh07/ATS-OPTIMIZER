from fastapi import FastAPI, UploadFile, File, Form
from app.services.parser.resume_parser import parse_resume
from app.services.matcher import match_resume_to_job
from app.services.scorer import score_match
import os
import tempfile

app = FastAPI()


def save_upload_to_temp(file: UploadFile, content: bytes) -> str:
    suffix = file.filename[file.filename.rfind("."):] if "." in file.filename else ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        return temp_file.name


@app.get("/")
def root():
    return {"message": "Welcome to my ATS Project!"}


@app.post("/parse-resume")
async def parse_resume_endpoint(
    file: UploadFile = File(...)
):
    content = await file.read()
    temp_path = save_upload_to_temp(file, content)

    try:
        return parse_resume(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/match-resume")
async def match_resume_endpoint(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    content = await file.read()
    temp_path = save_upload_to_temp(file, content)

    try:
        parsed_resume = parse_resume(temp_path)
        match_result = match_resume_to_job(parsed_resume, job_description)
        score_result = score_match(match_result)

        # Returning each layer separately keeps parser, matcher, and scorer easy to test.
        return {
            "parsed_resume": parsed_resume,
            "match_result": match_result,
            "score_result": score_result,
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

