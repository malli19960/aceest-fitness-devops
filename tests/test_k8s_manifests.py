from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = (
    ("rolling", "aceest-fitness-rolling", ("deployment.yaml",)),
    (
        "blue-green",
        "aceest-fitness-blue-green",
        ("deployment-blue.yaml", "deployment-green.yaml"),
    ),
    (
        "canary",
        "aceest-fitness-canary",
        ("deployment-stable.yaml", "deployment-canary.yaml"),
    ),
)


def load_manifest(path):
    with path.open(encoding="utf-8") as manifest_file:
        manifest = yaml.safe_load(manifest_file)
    assert isinstance(manifest, dict)
    assert manifest.get("apiVersion")
    assert manifest.get("kind")
    return manifest


@pytest.mark.parametrize(("strategy", "service_name", "deployment_files"), STRATEGIES)
def test_kubernetes_strategy_manifests_are_consistent(
    strategy, service_name, deployment_files
):
    strategy_dir = ROOT / "k8s" / strategy
    service = load_manifest(strategy_dir / "service.yaml")

    assert service["kind"] == "Service"
    assert service["metadata"]["name"] == service_name
    assert service["spec"]["type"] == "NodePort"

    selector = service["spec"]["selector"]
    assert selector.get("app")

    deployment_labels = []
    for filename in deployment_files:
        deployment = load_manifest(strategy_dir / filename)
        assert deployment["kind"] == "Deployment"

        pod_spec = deployment["spec"]["template"]
        labels = pod_spec["metadata"]["labels"]
        deployment_labels.append(labels)
        assert labels["app"] == selector["app"]

        container = pod_spec["spec"]["containers"][0]
        assert container["image"] == "__IMAGE__"
        assert container["readinessProbe"]["httpGet"]["path"] == "/health"
        assert container["livenessProbe"]["httpGet"]["path"] == "/health"

    if "slot" in selector:
        assert selector["slot"] in {
            labels["slot"] for labels in deployment_labels
        }
