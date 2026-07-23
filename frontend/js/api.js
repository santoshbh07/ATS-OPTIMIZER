const API_BASE_URL = "http://127.0.0.1:8000";

async function readErrorMessage(response) {
  try {
    const errorBody = await response.json();

    if (typeof errorBody.detail === "string") {
      return errorBody.detail;
    }
  } catch {
    return "The backend returned an unreadable error response.";
  }

  return "The backend could not analyze this resume.";
}

export async function analyzeResume(resumeFile, jobDescription) {
  if (!resumeFile || !jobDescription) {
    throw new Error("A resume file and job description are required.");
  }

  const formData = new FormData();
  formData.append("file", resumeFile);
  formData.append("job_description", jobDescription);

  let response;

  try {
    response = await fetch(`${API_BASE_URL}/match-resume`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error(
      "Could not reach the backend. Confirm FastAPI is running at http://127.0.0.1:8000 and refresh this page."
    );
  }

  if (!response.ok) {
    const errorMessage = await readErrorMessage(response);
    throw new Error(errorMessage);
  }

  return response.json();
}
