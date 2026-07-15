import re
from pathlib import Path

def test_openapi_operation_manifest_matches_sdk():
    yaml = (Path(__file__).parents[3] / "openapi" / "openapi.yaml").read_text()
    actual = sorted(re.findall(r"^\s+operationId:\s*([A-Za-z0-9_]+)\s*$", yaml, re.MULTILINE))
    expected = sorted(["health","listProjects","createProject","createOrigin","createDomainZone","listHostnames","createHostname","getHostname","deleteHostname","createWebhookEndpoint","createWidgetSession","getUsage"])
    assert actual == expected
