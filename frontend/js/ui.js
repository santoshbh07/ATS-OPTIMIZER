function clearElement(element) {
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = text;
  return element;
}

function createTagList(items, tagClassName) {
  const list = document.createElement("ul");
  list.className = "tag-list";

  if (!items.length) {
    const emptyItem = document.createElement("li");
    emptyItem.className = "tag";
    emptyItem.textContent = "None";
    list.appendChild(emptyItem);
    return list;
  }

  items.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.className = `tag ${tagClassName}`;
    listItem.textContent = item;
    list.appendChild(listItem);
  });

  return list;
}

function createDashboardCard(title, titleClassName) {
  const card = document.createElement("section");
  card.className = "dashboard-card";

  const heading = createTextElement("h3", titleClassName, title);
  card.appendChild(heading);
  return card;
}

function formatScore(score) {
  if (score === null || score === undefined) {
    return "N/A";
  }

  return `${score}%`;
}

function getScoreTone(score) {
  if (score >= 85) {
    return "excellent";
  }

  if (score >= 70) {
    return "good";
  }

  return "needs-work";
}

function getScoreLabel(score) {
  if (score === null || score === undefined) {
    return "Not Applicable";
  }

  if (score >= 85) {
    return "Excellent";
  }

  if (score >= 70) {
    return "Good Match";
  }

  return "Needs Work";
}

function getScoreDescription(scoreType, score) {
  if (score === null || score === undefined) {
    return "No relevant requirements were detected for this category.";
  }

  if (scoreType === "overall") {
    if (score >= 85) {
      return "Your resume is strongly aligned with this job.";
    }

    if (score >= 70) {
      return "Your resume has a good match with room for improvement.";
    }

    return "Your resume needs more alignment with this job.";
  }

  if (scoreType === "skills") {
    if (score >= 85) {
      return "Your resume includes most of the targeted skills.";
    }

    if (score >= 70) {
      return "Your resume includes several targeted skills.";
    }

    return "Your resume is missing several targeted skills.";
  }

  if (scoreType === "qualifications") {
    if (score >= 85) {
      return "Your qualifications strongly match the job requirements.";
    }

    if (score >= 70) {
      return "Your qualifications match many of the job requirements.";
    }

    return "Your resume may be missing important qualifications.";
  }

  return "";
}

function createScoreCard(label, score, description) {
  const card = document.createElement("article");
  const scoreTone = getScoreTone(score);
  card.className = `score-card ${scoreTone}`;

  const heading = createTextElement("h3", "", label);
  const body = document.createElement("div");
  body.className = "score-card-body";

  const meter = document.createElement("div");
  meter.className = "score-meter";
  meter.style.setProperty("--score-angle", `${score * 3.6}deg`);
  meter.appendChild(createTextElement("span", "score-number", String(score)));

  const scoreText = document.createElement("div");
  scoreText.className = "score-text";
  scoreText.append(
    createTextElement("p", "score-rating", getScoreLabel(score)),
    createTextElement("p", "score-description", description)
  );

  const denominator = createTextElement("span", "score-denominator", "/100");

  body.append(meter, denominator, scoreText);
  card.append(heading, body);
  return card;
}

function createKeywordCard(title, items, tagClassName, helperText, count) {
  const card = createDashboardCard(title, "");
  const header = card.querySelector("h3");

  if (count !== undefined) {
    const badge = createTextElement("span", "count-badge", String(count));
    header.appendChild(badge);
  }

  const list = createTagList(items, tagClassName);
  const helper = createTextElement("p", "card-helper", helperText);

  card.append(list, helper);
  return card;
}

function createRecommendationItem(title, description, toneClassName) {
  const item = document.createElement("li");
  item.className = `recommendation-item ${toneClassName}`;

  const content = document.createElement("div");
  content.append(
    createTextElement("strong", "", title),
    createTextElement("span", "", description)
  );

  const arrow = createTextElement("span", "recommendation-arrow", ">");

  item.append(content, arrow);
  return item;
}

function createRecommendationsCard() {
  const card = createDashboardCard("Recommendations", "with-star");
  const list = document.createElement("ul");
  list.className = "recommendation-list";

  list.append(
    createRecommendationItem(
      "Add more quantifiable achievements",
      "Include metrics to showcase impact.",
      "success"
    ),
    createRecommendationItem(
      "Include missing keywords naturally",
      "Use relevant keywords in context.",
      "warning"
    ),
    createRecommendationItem(
      "Enhance summary section",
      "Add a strong professional summary.",
      "accent"
    ),
    createRecommendationItem(
      "Check for consistency",
      "Ensure uniform formatting throughout.",
      "info"
    )
  );

  card.appendChild(list);
  return card;
}

export function setFieldError(fieldElement, errorElement, message) {
  const fieldGroup = fieldElement.closest(".field-group");
  errorElement.textContent = message;

  if (fieldGroup) {
    fieldGroup.classList.toggle("has-error", Boolean(message));
  }
}

export function setLoadingState(buttonElement, statusElement, isLoading) {
  buttonElement.disabled = isLoading;
  buttonElement.textContent = isLoading ? "Analyzing..." : "Analyze Resume";

  if (isLoading) {
    statusElement.textContent = "Analyzing resume against the job description...";
  }
}

export function renderEmptyState(resultsElement, statusElement) {
  clearElement(resultsElement);
  resultsElement.className = "empty-state";
  resultsElement.append(
    createTextElement("p", "empty-title", "No analysis yet."),
    createTextElement(
      "p",
      "empty-copy",
      "Upload a resume and paste a job description to see your dashboard."
    )
  );
  statusElement.textContent = "Results will appear after a resume is analyzed.";
}

export function renderApiError(resultsElement, statusElement, message) {
  clearElement(resultsElement);
  resultsElement.className = "empty-state error-state";
  resultsElement.appendChild(createTextElement("p", "", message));
  statusElement.textContent = "The analysis could not be completed.";
}

export function renderAnalysisResult(resultsElement, statusElement, result) {
  const scoreResult = result.score_result;
  const matchResult = result.match_result;

  clearElement(resultsElement);
  resultsElement.className = "dashboard-results";

  const scoreGrid = document.createElement("div");
  scoreGrid.className = "score-grid";
  scoreGrid.append(
    createScoreCard(
      "Overall ATS Score",
      scoreResult.overall_score,
      getScoreDescription("overall", scoreResult.overall_score)
    ),
    createScoreCard(
      "Keyword Match",
      scoreResult.skill_match_score,
      getScoreDescription("skills", scoreResult.skill_match_score)
    ),
    createScoreCard(
      "Qualification Match",
      scoreResult.qualification_match_score,
      getScoreDescription("qualifications", scoreResult.qualification_match_score)
    )
  );

  const insightGrid = document.createElement("div");
  insightGrid.className = "insight-grid";
  insightGrid.append(
    createKeywordCard(
      "Matched Keywords",
      matchResult.matched_skills,
      "matched",
      "Great. You have strong coverage of important keywords.",
      matchResult.matched_skills.length
    ),
    createKeywordCard(
      "Missing Keywords",
      [
        ...matchResult.missing_required_skills,
        ...matchResult.missing_preferred_skills,
      ],
      "missing",
      "Consider adding these keywords if you have experience with them.",
      matchResult.missing_required_skills.length +
        matchResult.missing_preferred_skills.length
    ),
    createKeywordCard(
      "Detected Skills",
      matchResult.resume_skills.all,
      "detected",
      "Skills extracted from your resume content."
    ),
    createRecommendationsCard()
  );

  const tip = createTextElement(
    "p",
    "dashboard-tip",
    "Tip: Tailor your resume to the job description. Use the missing keywords and recommendations to improve your score."
  );

  resultsElement.append(
    scoreGrid,
    insightGrid,
    tip
  );

  statusElement.textContent = `Analysis complete. Overall score: ${formatScore(
    scoreResult.overall_score
  )}.`;
}
