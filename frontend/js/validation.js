export const MAX_RESUME_FILE_SIZE = 5 * 1024 * 1024;

const allowedFileExtensions = [".pdf", ".docx"];
const minimumJobDescriptionLength = 40;

function getFileExtension(fileName) {
  const lastDotIndex = fileName.lastIndexOf(".");

  if (lastDotIndex === -1) {
    return "";
  }

  return fileName.slice(lastDotIndex).toLowerCase();
}

export function validateResumeFile(file) {
  if (!file) {
    return "Choose a resume file.";
  }

  const fileExtension = getFileExtension(file.name);

  if (!allowedFileExtensions.includes(fileExtension)) {
    return "Use a PDF or DOCX resume file.";
  }

  if (file.size > MAX_RESUME_FILE_SIZE) {
    return "Use a resume file smaller than 5 MB.";
  }

  return "";
}

export function validateJobDescription(jobDescription) {
  const trimmedDescription = jobDescription.trim();

  if (!trimmedDescription) {
    return "Paste a job description.";
  }

  if (trimmedDescription.length < minimumJobDescriptionLength) {
    return "Add more job-description details before analyzing.";
  }

  return "";
}

export function validateAnalysisForm(resumeFile, jobDescription) {
  return {
    resumeFile: validateResumeFile(resumeFile),
    jobDescription: validateJobDescription(jobDescription),
  };
}

export function hasValidationErrors(errors) {
  return Boolean(errors.resumeFile || errors.jobDescription);
}
