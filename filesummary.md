# ACEest Fitness & Gym — Project and Change Summary

This file records the purpose of the assignment files and the key changes made
to prepare the project for the DevOps submission.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Flask application with program, client-profile, workout-log, and progress-tracking APIs backed by SQLite. |
| `Versions/` | Progressive Flask snapshots covering app health, program catalog, detailed plans, client management, and activity tracking. |
| `tests/test_app.py` | Pytest coverage for calculations, programs, input validation, profile CRUD, workouts, progress, and SQLite behavior. |
| `requirements.txt` | Runtime dependencies: Flask and Gunicorn. |
| `requirements-dev.txt` | Development/test dependencies, including Pytest. |
| `Dockerfile` | Multi-stage container definition with a test target and a non-root Gunicorn runtime target. |
| `.dockerignore` | Excludes local and version-control files from the Docker build context. |
| `.github/workflows/main.yml` | GitHub Actions workflow for pushes and pull requests; compiles Python, tests in Docker, and builds the runtime image. |
| `Jenkinsfile` | Jenkins pipeline for SCM checkout, compilation, tests, test-container execution, and runtime image build. |
| `README.md` | Local setup, testing, Docker usage, and CI/Jenkins instructions. |
| `.gitignore` | Excludes Python caches, virtual environments, and local environment files from Git. |

## Recorded implementation changes

1. Kept the assignment-focused Flask entry point in `app.py` as the application
   source of truth.
2. Added finite, positive measurement validation and clear JSON `400` responses
   for invalid planning endpoint query values. Disabled Flask debug mode when
   starting the app directly.
3. Expanded the test suite to verify calculations, program schedules, available
   programs, endpoint responses, and invalid request values.
4. Separated runtime dependencies from development/test dependencies.
5. Added Docker test and runtime targets; the runtime image uses a non-root
   account and Gunicorn.
6. Updated GitHub Actions to run for all pushes and pull requests, compile the
   app and tests, run Pytest in the test image, and build the runtime image.
7. Updated Jenkins to use the job-configured SCM checkout rather than a
   placeholder repository URL, and aligned its build/test steps with the
   container workflow.
8. Updated `README.md` to document the local, Docker, GitHub Actions, and
   Jenkins workflows.
9. Added five progressive Flask snapshots under `Versions/` and documented
   their feature milestones in `README.md`; extended the sequence through
   detailed program data, client management, and workout/progress tracking.

## Validation notes

- `python -m pytest -q`: 33 tests passed during the implementation.
- `python -m compileall -q app.py tests Versions`: passed.
- Docker was not installed in the local workspace, so Docker image builds were
  not run locally. GitHub Actions and a configured Jenkins agent can run those
  image build checks.
