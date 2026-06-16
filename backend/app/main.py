from fastapi import FastAPI, UploadFile, File
from app.services.parser.resume_parser import parse_resume
import tempfile

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to my ATS Project!"}

@app.post("/parse-resume")
async def parse_resume_endpoint(
    file: UploadFile = File(...)
):
    
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=file.filename[file.filename.rfind("."):]
    ) as temp_file:

        content = await file.read()
        temp_file.write(content)

        temp_path = temp_file.name

    result = parse_resume(temp_path)

    return result