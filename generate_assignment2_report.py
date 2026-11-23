from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "2025TM93179_ACEest_Fitness_Assignment-2_Execution_and_Validation_Report.pdf"

BLUE = colors.HexColor("#184a78")
GREEN = colors.HexColor("#137547")
LIGHT_BLUE = colors.HexColor("#f4f7fb")
DARK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5b6475")
LINE = colors.HexColor("#d9e0ea")
AMBER = colors.HexColor("#fff8e7")


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="TitleCustom",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=26,
    leading=31,
    textColor=BLUE,
    alignment=TA_CENTER,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="SubtitleCustom",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=13,
    leading=18,
    textColor=MUTED,
    alignment=TA_CENTER,
    spaceAfter=16,
))
styles.add(ParagraphStyle(
    name="HeadingCustom",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=BLUE,
    spaceBefore=8,
    spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="BodyCustom",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=14,
    textColor=DARK,
    spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="SmallCustom",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8,
    leading=11,
    textColor=MUTED,
))
styles.add(ParagraphStyle(
    name="CaptionCustom",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8,
    leading=11,
    textColor=MUTED,
    alignment=TA_CENTER,
    spaceBefore=4,
    spaceAfter=10,
))


def p(text, style="BodyCustom"):
    return Paragraph(text, styles[style])


def heading(text):
    return Paragraph(text, styles["HeadingCustom"])


def table(headers, rows, widths=None):
    data = [[p(header, "SmallCustom") for header in headers]]
    for row in rows:
        data.append([p(str(value), "SmallCustom") for value in row])
    result = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfcfe")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return result


def callout(text):
    result = Table([[p(text)]], colWidths=[170 * mm])
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("LINEBEFORE", (0, 0), (0, -1), 4, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return result


def screenshot(filename, caption, max_width=160):
    path = ROOT / "execution_evidence" / filename
    if not path.exists():
        return p(f"Evidence image unavailable: {filename}", "CaptionCustom")
    image = Image(str(path))
    scale = min(max_width * mm / image.drawWidth, 105 * mm / image.drawHeight)
    image.drawWidth *= scale
    image.drawHeight *= scale
    image.hAlign = "CENTER"
    return [image, p(caption, "CaptionCustom")]


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(20 * mm, 15 * mm, 190 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 10 * mm, "ACEest Fitness & Gym | Assignment 2")
    canvas.drawRightString(190 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=20 * mm,
    leftMargin=20 * mm,
    topMargin=18 * mm,
    bottomMargin=20 * mm,
    title="ACEest Fitness - Assignment 2 Execution and Validation Report",
    author="Jampani Sreekara Mallikarjun",
)

story = []

story += [
    Spacer(1, 24 * mm),
    p("ACEest Fitness & Gym", "TitleCustom"),
    p("DevOps Assignment 2 - CI/CD Execution and Validation Report", "SubtitleCustom"),
    Spacer(1, 10 * mm),
    callout(
        "<b>Assignment status:</b> Jenkins, Docker, SonarQube configuration, "
        "Kubernetes manifests, GitHub Actions, and automated tests are implemented. "
        "Live Docker Hub, SonarQube, and cluster results must be captured in the "
        "configured Jenkins environment."
    ),
    Spacer(1, 18 * mm),
    p("<b>Name:</b> Jampani Sreekara Mallikarjun", "SubtitleCustom"),
    p("<b>Student ID:</b> 2025TM93179", "SubtitleCustom"),
    p("<b>Project:</b> malli19960/aceest-fitness-devops", "SubtitleCustom"),
    p("<b>Report date:</b> 23 November 2026", "SubtitleCustom"),
    p(
        '<b>GitHub repository:</b> <link href="https://github.com/malli19960/aceest-fitness-devops" '
        'color="#184a78"><u>https://github.com/malli19960/aceest-fitness-devops</u></link>',
        "SubtitleCustom",
    ),
    PageBreak(),
]

story += [
    heading("Report contents"),
    table(
        ["Section", "Content"],
        [
            ("1", "Solution and CI/CD architecture"),
            ("2", "Validation summary"),
            ("3", "Application and Docker evidence"),
            ("4", "GitHub Actions workflow"),
            ("5", "Jenkins pipeline"),
            ("6", "SonarQube quality gate"),
            ("7", "Kubernetes deployment strategies"),
            ("8", "Execution runbook"),
            ("9", "Docker Hub and live endpoint evidence"),
            ("10", "Challenges, mitigations, and submission checklist"),
        ],
        [25 * mm, 145 * mm],
    ),
    heading("1. Solution and CI/CD architecture"),
    p(
        "The project uses the main Flask application in <b>app.py</b>, a Docker "
        "test/runtime multi-stage build, Pytest, GitHub Actions, Jenkins, "
        "SonarQube, Docker Hub, and Kubernetes."
    ),
    table(
        ["Stage", "Implementation", "Result"],
        [
            ("Source", "GitHub main branch, webhook and Jenkins SCM polling", "Automated trigger"),
            ("Build and test", "Docker test target runs compile checks and Pytest", "36 local tests pass"),
            ("Code quality", "SonarScanner and SonarQube quality gate", "Configured; live result pending"),
            ("Image delivery", "Docker Hub tag build-number plus source revision", "Configured in Jenkins"),
            ("Deployment", "Rolling, blue-green, or canary Kubernetes strategy", "Manifests and rollback checks ready"),
            ("Verification", "Readiness/liveness probes and live /health smoke test", "Configured in Jenkins"),
        ],
        [30 * mm, 92 * mm, 48 * mm],
    ),
    p(
        "<b>Delivery flow:</b> Developer commit -&gt; GitHub webhook -&gt; Jenkins "
        "checkout -&gt; containerized Pytest -&gt; SonarQube/quality gate -&gt; Docker "
        "Hub image -&gt; Kubernetes deployment -&gt; health smoke test."
    ),
    PageBreak(),
]

story += [
    heading("2. Validation summary"),
    table(
        ["Check", "Status", "Evidence"],
        [
            ("Automated tests", "PASS - 36", "python -m pytest -q"),
            ("Kubernetes manifest tests", "PASS", "Three strategies and health probes validated"),
            ("Python compilation", "PASS", "app.py, tests, and Version snapshots compile"),
            ("Docker test target", "IMPLEMENTED", "Docker build --target test"),
            ("Docker runtime target", "IMPLEMENTED", "Non-root Gunicorn runtime"),
            ("GitHub Actions", "HISTORICAL PASS", "Run 11 for commit e48076a"),
            ("Jenkins Build #9", "HISTORICAL PASS", "Assignment 1 baseline; not an Assignment 2 deployment"),
            ("SonarQube gate", "PENDING LIVE RUN", "Requires Jenkins SonarQube server and webhook"),
            ("Docker Hub publish", "PENDING LIVE RUN", "Requires dockerhub-credentials"),
            ("Kubernetes deployment", "PENDING LIVE RUN", "Requires kubeconfig and cluster access"),
        ],
        [43 * mm, 38 * mm, 89 * mm],
    ),
    p(
        "The 36-test result includes 29 application tests and 7 Kubernetes manifest "
        "parameter cases, based on the current test suite."
    ),
    callout(
        "<b>Important evidence distinction:</b> Existing GitHub Actions Run 11 and "
        "Jenkins Build #9 evidence demonstrates the earlier Assignment 1 Docker "
        "pipeline. They do not prove Assignment 2 Docker Hub publishing, SonarQube "
        "quality-gate, or Kubernetes deployment."
    ),
    PageBreak(),
]

story += [
    heading("3. Application and container evidence"),
]
story += screenshot(
    "docker_vm_tests.jpg",
    "Historical Docker VM validation: daemon, test image, runtime image, and containerized test activity.",
)
story += screenshot(
    "validation_results.png",
    "Historical validation transcript. It is retained as baseline Assignment 1 evidence.",
)
story += [
    p(
        "<b>Container setup:</b> Docker builds use a test target and a non-root "
        "Gunicorn runtime target. The runtime image exposes port 5000 and stores "
        "SQLite data under /app/instance."
    ),
    p(
        "<b>Current limitation:</b> Kubernetes demo manifests do not include shared "
        "persistent storage. SQLite is suitable for demonstration only; production "
        "client data should migrate to a managed database."
    ),
    PageBreak(),
]

story += [
    heading("4. GitHub Actions workflow"),
]
story += screenshot(
    "github_actions_run_11_success.jpg",
    "GitHub Actions Run 11: successful push workflow for commit e48076a.",
)
story += [
    p(
        "The workflow in <b>.github/workflows/main.yml</b> runs on pushes and pull "
        "requests. It checks out the repository, compiles Python sources, builds "
        "the Docker test target, executes pytest in the container, and builds the "
        "runtime target."
    ),
    table(
        ["Workflow step", "Purpose"],
        [
            ("Checkout", "Retrieve the submitted revision"),
            ("Setup Python", "Install Python 3.11"),
            ("Install dependencies", "Install requirements-dev.txt"),
            ("Compile", "Validate Python source and test syntax"),
            ("Build test image", "Create aceest-fitness:test"),
            ("Run tests", "Execute the full Pytest suite in Docker"),
            ("Build runtime image", "Verify the production image"),
        ],
        [50 * mm, 120 * mm],
    ),
    PageBreak(),
]

story += [
    heading("5. Jenkins pipeline"),
]
story += screenshot(
    "jenkins_build_9_summary.jpg",
    "Historical Jenkins Build #9 summary. This run predates Assignment 2 deployment stages.",
)
story += [
    p(
        "The current <b>Jenkinsfile</b> uses a Multibranch Pipeline, GitHub push "
        "trigger support, Docker test and runtime builds, SonarQube analysis and "
        "quality gate, Docker Hub publishing, and Kubernetes deployment."
    ),
    table(
        ["Stage", "Behavior"],
        [
            ("Checkout", "Checks out SCM and creates a build-number/revision image tag"),
            ("Build and Test", "Builds the test target and runs Pytest inside it"),
            ("SonarQube Analysis", "Runs sonar-scanner with SonarQube server SonarQube"),
            ("Quality Gate", "Waits up to five minutes and aborts on failure"),
            ("Build and Push", "Publishes the runtime image on Docker Hub for main"),
            ("Deploy", "Executes the selected rolling, blue-green, or canary strategy"),
            ("Smoke and rollback", "Checks /health and reverses or removes failed deployment"),
        ],
        [45 * mm, 125 * mm],
    ),
    p(
        "<b>Required Jenkins credentials:</b> dockerhub-credentials "
        "(username/password) and kubeconfig (Secret file). Configure SonarScanner "
        "tool name SonarScanner and SonarQube server name SonarQube."
    ),
    PageBreak(),
]

story += [
    heading("6. SonarQube quality gate"),
    p(
        "The repository contains <b>sonar-project.properties</b> with the project "
        "key <b>aceest-fitness-devops</b>, Python 3.11 settings, source/test "
        "separation, and exclusions for generated caches and archived files."
    ),
    table(
        ["Configuration item", "Value"],
        [
            ("Project key", "aceest-fitness-devops"),
            ("Source", "Application repository"),
            ("Tests", "tests/**/*.py"),
            ("Exclusions", "Versions/**, Olderfiles/**, execution evidence, caches, SQLite"),
            ("Jenkins tool", "SonarScanner"),
            ("Jenkins server", "SonarQube"),
            ("Gate behavior", "waitForQualityGate abortPipeline: true"),
        ],
        [55 * mm, 115 * mm],
    ),
    p(
        "<b>Live evidence to capture:</b> SonarQube project overview, Quality Gate "
        "status, metrics, and Jenkins stage/build console output."
    ),
    PageBreak(),
]

story += [
    heading("7. Kubernetes deployment strategies"),
    table(
        ["Strategy", "Manifest behavior", "Rollback behavior"],
        [
            ("Rolling", "RollingUpdate, maxSurge 1, maxUnavailable 0", "kubectl rollout undo"),
            ("Blue-green", "Deploy inactive slot, health-check, then switch Service selector", "Keep active slot; scale failed target down"),
            ("Canary", "Canary pod beside stable pods, promote after smoke test", "Remove failed canary; undo stable promotion"),
        ],
        [28 * mm, 88 * mm, 54 * mm],
    ),
    p(
        "All Deployments use readiness and liveness probes on <b>/health</b>, "
        "resource requests/limits, non-privileged container settings, and dropped "
        "Linux capabilities."
    ),
    table(
        ["Service", "Type", "Purpose"],
        [
            ("aceest-fitness-rolling", "NodePort", "Rolling update demonstration"),
            ("aceest-fitness-blue-green", "NodePort", "Blue-green slot switch"),
            ("aceest-fitness-canary", "NodePort", "Canary-to-stable promotion"),
        ],
        [70 * mm, 35 * mm, 65 * mm],
    ),
    PageBreak(),
]

story += [
    heading("8. Jenkins and Kubernetes execution runbook"),
    p("<b>1. Configure Jenkins</b>"),
    p(
        "Create a Multibranch Pipeline for the repository. Configure Pipeline, "
        "GitHub, SonarQube Scanner, and Credentials plugins."
    ),
    p("<b>2. Add Jenkins credentials</b>"),
    p(
        "Add Docker Hub username/token under credential ID "
        "<b>dockerhub-credentials</b>. Add the cluster kubeconfig under "
        "<b>kubeconfig</b>."
    ),
    p("<b>3. Run one build for each strategy</b>"),
    p(
        "Open the main branch build page, select one parameter value "
        "(rolling, blue-green, or canary), and run the pipeline."
    ),
    p("<b>4. Verify Kubernetes resources</b>",),
]

code = (
    "kubectl get deployments,pods,services\n"
    "kubectl rollout status deployment/aceest-fitness --timeout=180s\n"
    "kubectl rollout status deployment/aceest-blue --timeout=180s\n"
    "kubectl rollout status deployment/aceest-green --timeout=180s\n"
    "kubectl rollout status deployment/aceest-stable --timeout=180s\n"
    "kubectl rollout status deployment/aceest-canary --timeout=180s"
)
pre = Table([[p(code.replace("\n", "<br/>"), "SmallCustom")]], colWidths=[170 * mm])
pre.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0d1117")),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#dbe4ee")),
    ("FONTNAME", (0, 0), (-1, -1), "Courier"),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [pre, PageBreak()]

story += [
    heading("9. Docker Hub and live endpoint evidence"),
    p(
        "Use the Jenkins build number and Git revision to identify immutable "
        "images, for example:"
    ),
    callout("<b>&lt;dockerhub-user&gt;/aceest-fitness:&lt;build-number&gt;-&lt;12-char-revision&gt;</b>"),
    p("<b>Minikube endpoint discovery:</b>"),
    p(
        "For a NodePort cluster, collect the node IP and NodePort, or for "
        "Minikube run the following commands:"
    ),
]
endpoint_code = (
    "minikube service aceest-fitness-rolling --url\n"
    "minikube service aceest-fitness-blue-green --url\n"
    "minikube service aceest-fitness-canary --url"
)
endpoint_pre = Table([[p(endpoint_code.replace("\n", "<br/>"), "SmallCustom")]], colWidths=[170 * mm])
endpoint_pre.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0d1117")),
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#dbe4ee")),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [
    endpoint_pre,
    p(
        "Record the Docker Hub tags and HTTP 200 <b>/health</b> responses for "
        "each strategy. Screenshots should show Jenkins stages, Docker Hub, "
        "SonarQube, Kubernetes resources, and endpoint responses."
    ),
    PageBreak(),
]

story += [
    heading("10. Challenges and mitigations"),
    table(
        ["Challenge", "Cause", "Mitigation"],
        [
            ("Docker access in Jenkins", "Jenkins lacked Docker socket permissions", "Administrator-approved docker group membership and Jenkins restart"),
            ("Credential exposure", "Registry and cluster access are secret", "Jenkins Credentials; no secrets in source"),
            ("Strategy isolation", "Shared labels could route wrong pods", "Distinct app and Service names"),
            ("Promotion failure", "A deployable image might fail at runtime", "Readiness/liveness probes and /health smoke checks"),
            ("SQLite replica state", "No shared database/storage in demo", "Document limitation; migrate to managed database"),
            ("Live assignment evidence", "Credentials and cluster are outside this workspace", "Capture new Jenkins, Docker Hub, SonarQube and Kubernetes outputs"),
        ],
        [48 * mm, 52 * mm, 70 * mm],
    ),
    heading("Submission checklist"),
]

checklist = [
    ("[ ]", "Public GitHub repository link"),
    ("[ ]", "Two-to-three-page markdown/PDF summary"),
    ("[ ]", "Jenkins pipeline successful build for main"),
    ("[ ]", "SonarQube project and quality-gate result"),
    ("[ ]", "Docker Hub repository with versioned images"),
    ("[ ]", "Rolling deployment evidence and endpoint"),
    ("[ ]", "Blue-green deployment evidence and endpoint"),
    ("[ ]", "Canary deployment evidence and endpoint"),
    ("[ ]", "Rollback/failed deployment test evidence"),
]
story += [
    table(["Done", "Submission item"], checklist, [18 * mm, 152 * mm]),
    Spacer(1, 8 * mm),
    callout(
        "<b>Final submission note:</b> Do not present the historical Assignment 1 "
        "Jenkins or GitHub evidence as live Assignment 2 deployment evidence. "
        "Capture fresh runs after the Docker Hub, SonarQube, and Kubernetes "
        "credentials are configured."
    ),
]

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(OUTPUT)
