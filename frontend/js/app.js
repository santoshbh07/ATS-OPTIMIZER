import { analyzeResume } from "./api.js";
import {
  hasValidationErrors,
  validateAnalysisForm,
  validateJobDescription,
  validateResumeFile,
} from "./validation.js";
import {
  renderAnalysisResult,
  renderApiError,
  renderEmptyState,
  setFieldError,
  setLoadingState,
} from "./ui.js";

const form = document.querySelector("#analysis-form");
const resumeFileInput = document.querySelector("#resume-file");
const jobDescriptionInput = document.querySelector("#job-description");
const resumeFileError = document.querySelector("#resume-file-error");
const jobDescriptionError = document.querySelector("#job-description-error");
const analyzeButton = document.querySelector("#analyze-button");
const clearDescriptionButton = document.querySelector("#clear-description-button");
const selectedFile = document.querySelector("#selected-file");
const statusMessage = document.querySelector("#status-message");
const resultsContent = document.querySelector("#results-content");

function getSelectedResumeFile() {
  return resumeFileInput.files.length > 0 ? resumeFileInput.files[0] : null;
}

function showValidationErrors(errors) {
  setFieldError(resumeFileInput, resumeFileError, errors.resumeFile);
  setFieldError(jobDescriptionInput, jobDescriptionError, errors.jobDescription);
}

function formatFileSize(sizeInBytes) {
  const sizeInKilobytes = sizeInBytes / 1024;

  if (sizeInKilobytes < 1024) {
    return `${Math.round(sizeInKilobytes)} KB`;
  }

  return `${(sizeInKilobytes / 1024).toFixed(1)} MB`;
}

function renderSelectedFile(file) {
  selectedFile.textContent = "";

  if (!file) {
    selectedFile.hidden = true;
    return;
  }

  const fileName = document.createElement("span");
  fileName.className = "selected-file-name";
  fileName.textContent = file.name;

  const fileSize = document.createElement("span");
  fileSize.className = "selected-file-size";
  fileSize.textContent = formatFileSize(file.size);

  const fileStatus = document.createElement("span");
  fileStatus.className = "selected-file-status";
  fileStatus.textContent = "Selected";

  selectedFile.append(fileName, fileSize, fileStatus);
  selectedFile.hidden = false;
}

async function handleFormSubmit(event) {
  event.preventDefault();

  const resumeFile = getSelectedResumeFile();
  const jobDescription = jobDescriptionInput.value;
  const validationErrors = validateAnalysisForm(resumeFile, jobDescription);

  showValidationErrors(validationErrors);

  if (hasValidationErrors(validationErrors)) {
    statusMessage.textContent = "Fix the form errors before analyzing.";
    return;
  }

  setLoadingState(analyzeButton, statusMessage, true);

  try {
    const result = await analyzeResume(resumeFile, jobDescription);
    renderAnalysisResult(resultsContent, statusMessage, result);
  } catch (error) {
    renderApiError(resultsContent, statusMessage, error.message);
  } finally {
    setLoadingState(analyzeButton, statusMessage, false);
  }
}

function handleResumeFileChange() {
  const selectedResumeFile = getSelectedResumeFile();
  const errorMessage = validateResumeFile(selectedResumeFile);
  renderSelectedFile(selectedResumeFile);
  setFieldError(resumeFileInput, resumeFileError, errorMessage);
}

function handleJobDescriptionInput() {
  const errorMessage = validateJobDescription(jobDescriptionInput.value);
  setFieldError(jobDescriptionInput, jobDescriptionError, errorMessage);
}

function handleClearDescriptionClick() {
  jobDescriptionInput.value = "";
  setFieldError(jobDescriptionInput, jobDescriptionError, "");
  jobDescriptionInput.focus();
}

form.addEventListener("submit", handleFormSubmit);
resumeFileInput.addEventListener("change", handleResumeFileChange);
jobDescriptionInput.addEventListener("input", handleJobDescriptionInput);
clearDescriptionButton.addEventListener("click", handleClearDescriptionClick);

renderEmptyState(resultsContent, statusMessage);
