"""Custom authorizer, and consistency between the frontend and the deployed API routes."""
import re
from pathlib import Path

import pytest
import yaml

from conftest import add_person

ROOT = Path(__file__).resolve().parents[2]
METHOD_ARN = "arn:aws:execute-api:eu-central-1:123456789012:abc123/dev/POST/user/readitem"


def test_authorizer_allows_own_user_routes_and_returns_id(load, vacc):
    authorizer = load("lambdaAuthorizer")
    add_person(vacc, 42, 2, Mail="max@example.com", secret="pwhash")

    result = authorizer.lambda_handler(
        {"authorizationToken": "max@example.com|pwhash", "methodArn": METHOD_ARN}, None)

    [statement] = result["policyDocument"]["Statement"]
    assert statement["Effect"] == "Allow"
    assert statement["Resource"] == ["arn:aws:execute-api:eu-central-1:123456789012:abc123/dev/POST/user/*"]
    assert result["context"] == {"ID": 42}


@pytest.mark.parametrize("token", ["max@example.com|wrong", "nobody@example.com|pwhash", "malformed"])
def test_authorizer_rejects_invalid_tokens(load, vacc, token):
    authorizer = load("lambdaAuthorizer")
    add_person(vacc, 42, 2, Mail="max@example.com", secret="pwhash")

    with pytest.raises(Exception, match="Unauthorized"):
        authorizer.lambda_handler({"authorizationToken": token, "methodArn": METHOD_ARN}, None)


def deployed_routes():
    class Loader(yaml.SafeLoader):
        pass
    Loader.add_multi_constructor("!", lambda loader, suffix, node: None)
    config = yaml.load((ROOT / "backend" / "serverless.yml").read_text(), Loader=Loader)
    return {event["http"]["path"]
            for fn in config["functions"].values()
            for event in fn.get("events", []) if "http" in event}


def test_every_frontend_api_call_targets_a_deployed_route():
    called = set()
    for page in (ROOT / "frontend").rglob("*.*"):
        if page.suffix in {".html", ".js"}:
            called |= set(re.findall(r"execute-api\.[^/]+/dev/((?:user|admin)/\w+)", page.read_text()))

    # user/dummy is only the X-editable placeholder URL; without a `pk` X-editable never calls it
    called.discard("user/dummy")
    assert called, "no API calls found"
    assert called <= deployed_routes(), f"unknown routes: {sorted(called - deployed_routes())}"
