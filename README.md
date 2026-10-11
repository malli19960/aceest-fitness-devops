# ACEest Fitness & Gym

ACEest is a lightweight Flask-based fitness application designed for gym planning and client guidance. The project demonstrates a complete DevOps workflow covering development, testing, containerization, and automation.

## Features

- Fitness program recommendations
- Detailed weekly workout plans with exercises, sets, reps, rest times, and focus
- Meal plans with estimated calories and protein
- BMI estimation and goal-based calorie guidance
- SQLite-backed client profiles, workout logs, and progress/adherence tracking
- REST endpoints for health checks, programs, clients, workouts, and progress
- Pytest test suite
- Docker container support
- GitHub Actions CI workflow
- Jenkins pipeline configuration

## Project Structure

- `app.py` – Flask application
- `Versions/` – standalone Flask snapshots showing features added over time
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
python -m compileall -q app.py tests Versions
```

`requirements.txt` contains runtime dependencies. `requirements-dev.txt` adds
Pytest for local and CI validation.

## Progressive Flask Versions

The standalone scripts in `Versions/` show the application's development in
feature steps. `app.py` remains the main, fully tested application used by
Docker, Jenkins, and GitHub Actions.

| Version | Added features |
| --- | --- |
| `app_v1_0.py` | Initial Flask application and home endpoint. |
| `app_v1_1.py` | Adds service health endpoint and location metadata. |
| `app_v2_0.py` | Adds the fitness-program catalog endpoint. |
| `app_v2_1.py` | Adds BMI, calorie guidance, program recommendation, and a basic weekly plan endpoint. |
| `app_v3_0.py` | Adds the complete weekly plan and summary endpoints with validated inputs. |
| `app_v3_1.py` | Expands each program with exercise sets/reps/rest, meal calories and protein, and detailed weekly schedules. |
| `app_v4_0.py` | Adds SQLite-backed client profile create/read/update/delete routes, including BMI and calorie summaries. |
| `app_v5_0.py` | Adds persistent workout logs and progress/adherence records to client profiles. This is the complete feature set used by `app.py`. |

To run a snapshot from the project root, for example:

```bash
python Versions/app_v1_0.py
```

Stop that server before running another snapshot because they all use port 5000.
The snapshots use the same installed Flask runtime dependency as the main app.
The version 3.1 to 5.0 snapshots use the shared application implementation
with features enabled to match each milestone.

## API Features

### Programs and plans

- `GET /api/programs` returns four programs with weekly workout outlines,
  exercise examples (sets, reps, rest and focus), meal suggestions, estimated
  calories and protein, and program focus.
- `GET /api/plan?goal=fat%20loss&height=175&weight=70&age=28` returns a BMI
  estimate/category, estimated calorie target, recommended program and weekly
  schedule.
- `GET /api/summary` returns a compact client profile and recommendation.

Nutrition and calorie numbers are general estimates, not medical advice.

### Client management and tracking

`POST /api/clients` creates a client profile. Required JSON fields are `name`,
`age`, `height_cm`, `weight_kg`, and `goal`; `experience` is optional:

```json
{
  "name": "Asha Kumar",
  "age": 29,
  "height_cm": 168,
  "weight_kg": 64,
  "goal": "fat loss",
  "experience": "beginner"
}
```

Other profile routes:

- `GET /api/clients` lists profiles with calculated BMI and calorie targets.
- `GET /api/clients/<id>` retrieves one profile.
- `PUT /api/clients/<id>` updates profile fields using the same required fields.
- `DELETE /api/clients/<id>` removes the profile and its associated tracking records.

Log workouts with `POST /api/clients/<id>/workouts` using `workout_type` and
positive `duration_min`; `workout_date` (`YYYY-MM-DD`) and `notes` are optional.
Use `GET` on the same route to retrieve a client's workout history.

Record weight and adherence with `POST /api/clients/<id>/progress` using
`weight_kg` and `adherence_pct` (integer from 0 to 100); `notes` is optional.
Use `GET /api/clients/<id>/progress` to retrieve progress history.

Client, workout, and progress records are persisted to SQLite at
`instance/aceest_fitness.db` by default. Tests can override the database path.
When running in Docker, mount a volume at `/app/instance` if you need the
records to survive container replacement.

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

On the Linux assignment VM, start Docker and verify the daemon before building:

```bash
sudo systemctl start docker
systemctl is-active docker
id -nG
```

The daemon check should print `active`. The interactive VM account must have
Docker access (in this VM, it is a member of the `docker` group). From the
repository directory, build the test image and run its tests:

```bash
docker build --target test -t aceest-fitness:test .
docker run --rm aceest-fitness:test
```

Build and launch the runtime image on port 5000, then verify the service before
stopping and removing the temporary container:

```bash
docker build --target runtime -t aceest-fitness:latest .
docker run -d --name aceest-fitness-runtime -p 5000:5000 aceest-fitness:latest
curl http://127.0.0.1:5000/health
curl "http://127.0.0.1:5000/api/plan?weight=70&height=175&age=30&gender=male&activity=moderate&goal=fat_loss"
docker stop aceest-fitness-runtime
docker rm aceest-fitness-runtime
```

The assignment VM validation completed successfully: both image targets built,
all 33 tests passed in the test container, and a temporary runtime container
returned HTTP 200 from `/health` and `/api/plan` on port 5000. The container
was stopped and removed after the smoke check. Docker group membership grants
effectively root-level host control; use only the VM's administrator-approved
access.

## GitHub Actions Workflow

The workflow in `.github/workflows/main.yml` runs on every push and pull
request. It performs the following steps:

1. Checks out the repository
2. Installs Python development dependencies and compiles the app, tests, and
   version snapshots
3. Builds the test image and runs Pytest inside that container
4. Builds the production runtime image

This ensures that code changes are validated before merging and that both
container targets build successfully.

The initial complete-application push (commit `4a79a34`) passed in
[GitHub Actions run 4](https://github.com/malli19960/aceest-fitness-devops/actions/runs/38119817980).
A later workflow run, run 11, also passed
compilation, containerized tests, and both image builds for report commit
`e48076a`:
[GitHub Actions run 11](https://github.com/malli19960/aceest-fitness-devops/actions/runs/38124593209).

## Git Workflow

Clone the repository and move into the project directory:

```bash
git clone https://github.com/malli19960/aceest-fitness-devops.git
cd aceest-fitness-devops
```

Before committing local changes, check the current branch and review what will
be included:

```bash
git status
git diff
```

Stage the intended application, test, CI, and documentation files, then commit
and push them to `main`:

```bash
git add app.py tests Versions Dockerfile .dockerignore .gitignore \
  requirements.txt requirements-dev.txt Jenkinsfile README.md \
  .github/workflows/main.yml fitness_gui_demo.py filesummary.md \
  execution_validation_report.html execution_evidence
git diff --cached --check
git diff --cached --stat
git commit -m "Add complete ACEest Fitness application and DevOps workflow"
git push origin main
```

After pushing, verify the branch and commit on GitHub. GitHub Actions is
configured to run on pushes and pull requests. Keep credentials, `.env` files,
local databases, and generated caches out of commits; review the staged diff
before committing.

## Jenkins Integration

Configure a Jenkins Pipeline or Multibranch Pipeline job to use this repository
and the `Jenkinsfile`. Install the Jenkins Pipeline and GitHub plugins, then
configure a GitHub webhook pointing to `https://<jenkins-host>/github-webhook/`
for push events. The Jenkins agent must have Docker installed and access to its
daemon; Python and Pytest are provided by the Docker test image. Jenkins checks
out the configured SCM repository (no repository URL is hard-coded) and
performs these stages:

1. Build the test image, compiling the app and tests during the image build.
   The Jenkins stage is named **Build and Lint**, but currently runs the Docker
   test-image build only; it does not run a separate linter.
2. Run Pytest in the test container
3. Build the runtime image

This provides a second quality gate in a controlled Jenkins build environment.
The current pipeline builds and validates images; it does not deploy or leave
the application running as a service.

For a regular Pipeline job, select **Pipeline script from SCM**, choose **Git**,
set the repository URL to
`https://github.com/malli19960/aceest-fitness-devops.git`, use branch
specifier `*/main`, and set the script path to `Jenkinsfile`. Enable **GitHub
hook trigger for GITScm polling** when using the GitHub webhook.

In the assignment VM, the first Jenkins pipeline attempts failed because the
Jenkins service account could not access `/var/run/docker.sock`, even though
the interactive VM user could. An administrator added `jenkins` to the
`docker` group and restarted Jenkins so the service acquired the supplementary
group membership. The resulting checks confirmed `id jenkins` included
`docker`, and `sudo -u jenkins docker info` successfully reported Docker Engine
27.5.1. For an administrator-approved setup, the corresponding commands are:

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
id jenkins
sudo -u jenkins docker info --format '{{.ServerVersion}}'
```

To execute the job, sign in to the VM's Jenkins web interface, open
**ACEest Fitness Gym-CI**, choose **Build Now**, then open the new build's
**Console Output**. The `Jenkinsfile` runs **Build and Lint**, **Test**, and
**Build Runtime Image** in that order. Build #9 completed with **SUCCESS**,
with all 33 tests passing in the Test stage; [view its Console Output in the VM](http://localhost:8080/job/ACEest%20Fitness%20Gym-%20CI/9/console).
For automatic runs, enable **GitHub hook trigger
for GITScm polling** and configure the repository webhook to point to
`https://<jenkins-host>/github-webhook/`.

The submission report embeds three fresh screenshots from Build #9: the
successful build summary, the test stage showing 33 passing tests, and the
final console output showing `Finished: SUCCESS`. The earlier Build #2
permission-denied screenshot is retained as historical context.

**Security note:** membership in the `docker` group effectively grants
root-level control of the host. This VM change was performed by its
administrator; use a dedicated Docker-capable agent instead where policy does
not permit Docker access for the Jenkins service. The Jenkins Build #2
screenshot in the report is historical evidence of the original permission
failure; Build #9 is the later successful run. The Docker VM screenshots show
the manual image builds, test run, and runtime API checks. GitHub Actions also
validates the Docker targets on pushes.

## Assignment Mapping

This project maps to the DevOps assignment requirements by implementing:

- Flask application development
- Automated code validation with pytest
- Docker-based packaging
- Jenkins build automation
- GitHub Actions CI pipeline
- Documentation for setup and execution
