# ATS Optimizer Frontend Plan

## Technology

The frontend will use:

- HTML
- CSS
- Vanilla JavaScript
- ES modules

The first version will not use React, TypeScript, Tailwind CSS, Bootstrap, or a
frontend build system.

## Goal

Create an understandable and responsive frontend that works with mock ATS
analysis data first and can later connect to the existing Python backend.

## Core User Workflow

1. The user opens the ATS Optimizer.
2. The user selects a PDF or DOCX resume.
3. The user pastes a job description.
4. The frontend validates both inputs.
5. The user starts the analysis.
6. The frontend displays a loading state.
7. The mock API returns a realistic result.
8. The frontend displays scores, keywords, and recommendations.
9. Later, the mock API is replaced with a real Python API request.

## Phase 1 — Static Foundation

Create:

- Application header
- Introductory section
- Resume upload field
- Job-description textarea
- Analyze button
- Empty results section
- Footer
- Responsive layout

No analysis behavior should be implemented during this phase.

## Phase 2 — Form Validation

Implement:

- Required resume validation
- Required job-description validation
- PDF and DOCX file-type validation
- File-size validation
- Clear field-level error messages
- Accessible error messages
- Removal of errors after correction

## Phase 3 — Mock Analysis Service

Implement:

- api.js service function
- Mock request delay
- Mock success response
- Mock failure response for testing
- Loading state
- Error state
- Retry behavior

Mock data must not be imported directly into app.js.

## Phase 4 — Analysis Results

Display:

- File name
- Overall ATS score
- Keyword match score
- Formatting score
- Matched keywords
- Missing keywords
- Detected skills
- Section feedback
- Recommendations

The recommendations must not encourage users to claim skills or experience they
do not actually have.

## Phase 5 — Python API Integration

After the frontend workflow works with mock data:

- Inspect existing backend endpoints
- Define the final request and response format
- Update api.js to use fetch()
- Send the resume using FormData
- Send the job description
- Handle backend errors
- Configure CORS if required

Do not implement database persistence during this phase.

## Phase 6 — Database Integration

This phase will begin only after database concepts have been learned and the
database design has been approved.

Potential future functionality:

- Save an analysis
- List previous analyses
- Retrieve a saved analysis
- Delete an analysis

This phase is intentionally postponed.

## Out of Scope for the Initial Frontend

- Authentication
- User profiles
- Payments
- Subscriptions
- Multiple organizations
- Resume version control
- AI chat
- Analysis history
- Database persistence
- Admin dashboard