# ATS Optimizer — Codex Instructions

## Project Overview

This repository contains an ATS Resume Optimizer.

The existing application backend is written in Python. Its current structure
includes schemas, resume parsing services, keyword matching, scoring, and tests.

A new frontend will be added using:

- HTML
- CSS
- Vanilla JavaScript with ES modules

Do not introduce React, TypeScript, Next.js, Vue, Angular, Tailwind CSS,
Bootstrap, or another frontend framework unless explicitly requested.

## Current Development Priority

The current priority is building a frontend while the project owner reviews
JavaScript and studies database development.

The frontend must initially work with realistic mock analysis results.

The database implementation is intentionally postponed.

## Existing Backend

The existing backend code is functional project code and must not be
reorganized or rewritten without an explicit request.

Important existing areas include:

- backend/app/main.py
- backend/app/schemas/
- backend/app/services/
- backend/app/services/parser/
- backend/tests/

Before changing backend code, inspect the relevant modules and explain why a
backend change is necessary.

## Database Restriction

An existing database file or module is intentionally empty.

Before making changes, identify and report its exact path.

Do not:

- Modify the empty database file
- Add database connections
- Add database models
- Add SQLAlchemy
- Add migrations
- Add database dependencies
- Import the empty database module elsewhere
- Delete or rename the database file
- Implement temporary database behavior

Database implementation is outside the current scope.

## Frontend Location

The frontend must be created in a root-level directory:

frontend/

Do not place frontend files inside backend/app/.

The intended frontend structure is:

frontend/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── app.js
│   ├── api.js
│   ├── validation.js
│   ├── ui.js
│   └── mock-data.js
└── assets/

## Frontend Responsibilities

### index.html

Contains the semantic page structure and accessible form elements.

### css/styles.css

Contains the visual design, responsive layout, component states, and reusable
CSS classes.

### js/app.js

Coordinates the application workflow and registers event listeners.

### js/validation.js

Contains validation functions for resume files and job descriptions.

### js/ui.js

Contains DOM-rendering and interface-state functions.

### js/api.js

Provides the frontend service layer.

It must initially return mock results. Later, it will be changed to communicate
with the Python API.

### js/mock-data.js

Contains realistic temporary ATS analysis results.

Page-level code must not import mock data directly. Mock data must be accessed
through api.js.

## JavaScript Learning Requirements

The project owner is reviewing JavaScript and must be able to understand and
maintain the generated code.

When writing JavaScript:

- Prefer simple and readable code
- Use descriptive variable and function names
- Use ES modules
- Avoid the `var` keyword
- Avoid unnecessary classes
- Avoid clever one-line implementations
- Avoid unexplained advanced patterns
- Keep functions small and focused
- Explain important JavaScript concepts introduced
- Add comments only when the reasoning is not obvious
- Do not generate very large files without dividing responsibilities

Important concepts should be introduced clearly:

- DOM selection
- Event handling
- preventDefault()
- File objects
- Arrays and objects
- ES module imports and exports
- Promises
- async/await
- try/catch/finally
- fetch()
- FormData
- Error handling

## HTML Requirements

- Use semantic HTML
- Associate every input with a label
- Use correct button types
- Support keyboard navigation
- Use accessible status and error messages
- Do not use inline JavaScript
- Do not use inline CSS

## CSS Requirements

- Use plain CSS
- Use CSS custom properties for repeated design values
- Make the interface responsive
- Avoid unnecessary animations
- Avoid excessive absolute positioning
- Maintain visible keyboard focus styles
- Organize CSS into understandable sections

## Frontend States

The interface must eventually support:

- Initial state
- Empty state
- Validation errors
- Loading state
- Success state
- API error state
- Retry state

Do not only design the success state.

## File Upload Rules

The frontend may initially accept:

- PDF
- DOCX

The frontend should enforce a reasonable file-size limit.

Frontend validation is only for user experience. The Python backend must later
perform its own security validation.

## Privacy and Security

- Do not commit uploaded resumes
- Do not store resume contents in localStorage
- Do not store job descriptions in localStorage without an explicit request
- Do not log resume contents
- Do not log personal document contents
- Treat uploaded content as untrusted
- Do not render user-controlled HTML
- Prefer textContent or safe DOM element creation over innerHTML
- Never commit secrets or API keys
- Do not claim mock validation is production security

## Existing Python Code

Do not modify unrelated Python files while building the frontend.

Do not modify the parser, matcher, scorer, schemas, or API entry point unless
the current task explicitly requires it.

Do not rename existing functions merely for style consistency.

Do not perform broad refactoring during frontend tasks.

## Tests

The repository appears to contain more than one tests directory.

Before moving, deleting, or consolidating tests:

1. Inspect both locations.
2. Explain what each directory tests.
3. Identify whether either directory is obsolete.
4. Ask for explicit approval before restructuring them.

Never delete or weaken tests merely to make a task pass.

## Virtual Environment and Generated Files

Do not modify files inside venv/.

Do not commit:

- venv/
- __pycache__/
- *.pyc
- uploaded resumes
- environment files containing secrets

If these are not already excluded, recommend appropriate .gitignore entries.

## Required Workflow

Before implementation:

1. Read this AGENTS.md file.
2. Inspect files relevant to the task.
3. Explain the current behavior.
4. Propose a small implementation plan.
5. State assumptions.
6. Identify files that will be created or modified.
7. Keep the scope limited to the requested task.

After implementation:

1. List every created or modified file.
2. Explain the purpose of each change.
3. Run relevant tests or checks.
4. Report exact command results.
5. Explain how to manually test the feature.
6. Report limitations or unfinished work honestly.

## Scope Restrictions

Do not implement the following unless explicitly requested:

- Database functionality
- Authentication
- User accounts
- Payments
- Subscriptions
- Deployment configuration
- External AI integrations
- React or another frontend framework
- Major backend refactoring
- Resume storage
- Analysis history persistence

When a task appears to require work outside its stated scope, report the issue
before expanding the implementation.