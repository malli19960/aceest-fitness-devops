# ACEest Fitness & Gym — DevOps Assignment 2

**Student:** Jampani Sreekara Mallikarjun

**Student ID:** 2025TM93179

**Repository:** https://github.com/malli19960/aceest-fitness-devops

**Report date:** 23 November 2026

## 1. Objective and architecture

This project extends the Assignment 1 Flask fitness application into an
automated build, quality-validation, image-publishing, and Kubernetes
deployment workflow. The existing Flask API, pytest suite, Dockerfile, and
GitHub Actions workflow remain the application and CI foundation.

The delivery path is:

1. A developer pushes a change to GitHub.
2. GitHub Actions compiles the Flask application and tests, runs the
   containerized pytest suite, and builds the runtime Docker image.
3. A Jenkins Multibranch Pipeline checks out the selected revision, builds and
   tests the container, runs SonarQube analysis, and waits for the configured
   quality gate.
4. On `main`, Jenkins builds a runtime image tagged with the build number and
   source revision, then publishes it to the ACEest Docker Hub repository.
5. Jenkins deploys that immutable tag to the configured Kubernetes cluster
   using the requested rolling, blue-green, or canary strategy. Readiness
   probes gate rollout progress; failed rolling or canary promotions are
   reverted or removed.

The pipeline uses Jenkins credentials rather than embedding Docker Hub tokens
or Kubernetes credentials in source code. The required credential IDs and
Jenkins tool/server names are documented in the project README.

## 2. Deployment strategies

Three strategy-specific Kubernetes Services allow the demonstrations to run
side by side in one namespace:

- **Rolling update:** Kubernetes replaces pods gradually, keeping at least one
  available during the update. Jenkins waits for the rollout and calls
  `kubectl rollout undo` if it does not complete.
- **Blue-green:** Jenkins prepares the inactive color and waits for it to pass
  its readiness checks before changing the Service selector. If preparation
  fails, the Service continues routing to the previously active color.
- **Canary:** A single canary replica is added beside two stable replicas for
  a readiness check. After a successful check, the new image is promoted to
  the stable Deployment and the canary is scaled down. Kubernetes Service
  balancing is connection-based and does not guarantee a precise canary
  traffic percentage.

The manifests include HTTP readiness and liveness probes on `/health`, CPU and
memory requests/limits, and a container security context that disables
privilege escalation and drops Linux capabilities.

## 3. Challenges and mitigations

**Managing credentials safely.** CI/CD requires registry and cluster access.
The pipeline retrieves a Docker Hub access token and kubeconfig from Jenkins
Credentials at runtime; neither is committed to the repository. The cluster
identity should be restricted to the application namespace and required
Deployment and Service operations.

**Keeping the strategies isolated.** Shared labels or Service names could
route requests to pods from another strategy. Each strategy therefore uses a
distinct app label and Service name so the three deployment demonstrations do
not select one another's pods.

**Checking health before promotion.** A successful image build alone does not
show that the application starts in the target environment. Kubernetes probes
check the Flask `/health` endpoint, and Jenkins waits for rollout status before
switching blue-green traffic or promoting the canary.

**SQLite and replicas.** The current application persists records to a local
SQLite file. These demo manifests do not mount shared persistent storage, so
replica data is not shared and may be lost when pods are replaced. This is
explicitly documented as a limitation; a production rollout should migrate
application persistence to a managed relational database before scaling or
using real client records.

## 4. Automation outcomes and evidence

Assignment 1 validation provides a baseline of **36 passing pytest tests**,
including application behavior and Kubernetes manifest consistency checks.
The repository also contains prior evidence of successful Jenkins and GitHub
Actions runs for that version.

**Assignment 2 implementation status:** The Jenkins pipeline, SonarQube
project configuration, Kubernetes strategy manifests, and operator
instructions have been added to the project. A running Assignment 2 cluster
has not yet been validated in this report. Before submission, run the Jenkins
pipeline for all three `DEPLOYMENT_STRATEGY` choices and replace this status
with the observed build numbers, SonarQube quality-gate result, Docker Hub
image tags, Kubernetes rollout results, and reachable `/health` endpoint URLs.
Attach screenshots or other run evidence from the VM; do not treat these
configuration files as proof of a successful live deployment.
