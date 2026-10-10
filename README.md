# ACEest Fitness & Gym

ACEest is a lightweight Flask-based fitness application designed for gym planning and client guidance. The project demonstrates a complete DevOps workflow covering development, testing, containerization, and automation.

## Features

- Fitness program recommendations
- BMI estimation and workout planning
- Daily calorie guidance
- REST endpoints for health checks and program generation
- Pytest test suite
- Docker container support
- GitHub Actions CI workflow
- Jenkins pipeline configuration

## Project Structure

- `app.py` – Flask application
- `requirements.txt` – Python dependencies
- `tests/test_app.py` – Pytest test suite
- `Dockerfile` – Container image definition
- `.github/workflows/main.yml` – GitHub Actions pipeline
- `Jenkinsfile` – Jenkins pipeline configuration

## Local Setup

1. Clone this repository.
2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

4. Run the Flask app:

   ```bash
   python app.py
   ```

5. Open the application in a browser or test via curl:

   ```bash
   http://127.0.0.1:5000/health
   ```

## Running Tests

```bash
python -m pytest -q
python -m compileall -q app.py tests
```

`requirements.txt` contains runtime dependencies. `requirements-dev.txt` adds
Pytest for local and CI validation.

## Docker Usage

Build the image:

```bash
docker build --target runtime -t aceest-fitness:latest .
```

Run the container:

```bash
docker run -p 5000:5000 aceest-fitness:latest
```

The runtime image runs Gunicorn as a non-root user. To build and run the
containerized test suite:

```bash
docker build --target test -t aceest-fitness:test .
docker run --rm aceest-fitness:test
```

## GitHub Actions Workflow

The workflow in `.github/workflows/main.yml` runs on every push and pull
request. It performs the following steps:

1. Checks out the repository
2. Installs Python development dependencies and compiles the app and tests
3. Builds the test image and runs Pytest inside that container
4. Builds the production runtime image

This ensures that code changes are validated before merging and that both
container targets build successfully.

## Jenkins Integration

Configure a Jenkins Pipeline or Multibranch Pipeline job to use this repository
and the `Jenkinsfile`. Install the Jenkins Pipeline and GitHub plugins, then
configure a GitHub webhook pointing to `https://<jenkins-host>/github-webhook/`
for push events. The Jenkins agent must have Python 3.11, pip, and access to a
Docker daemon. The pipeline uses Jenkins SCM checkout (no repository URL is
hard-coded) and performs these stages:

1. Checkout source code
2. Install development dependencies and compile the app and tests
3. Run Pytest
4. Build the test image, run its tests, and build the runtime image

This provides a second quality gate in a controlled Jenkins build environment.

## Assignment Mapping

This project maps to the DevOps assignment requirements by implementing:

- Flask application development
- Automated code validation with pytest
- Docker-based packaging
- Jenkins build automation
- GitHub Actions CI/CD pipeline
- Documentation for setup and execution
