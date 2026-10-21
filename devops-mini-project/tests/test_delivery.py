import threading
from urllib.parse import parse_qs, urlsplit
import pytest
from werkzeug.serving import make_server
from app import create_app
from scripts.verify_release import verify
from scripts.deploy_render import build_hook_url

@pytest.fixture
def service():
    server = make_server("127.0.0.1", 0, create_app({"APP_VERSION": "new-sha"}))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:" + str(server.server_port)
    server.shutdown()
    thread.join(timeout=2)
    server.server_close()

def test_live_http_verification_accepts_expected_version(service):
    assert verify(service, "new-sha", timeout=3, interval=.01)["version"] == "new-sha"

def test_live_http_verification_rejects_old_release(service):
    with pytest.raises(RuntimeError, match="timed out"):
        verify(service, "old-sha", timeout=.03, interval=.01)

@pytest.mark.parametrize("url", ["localhost:5000", "file:///tmp/a", "https://example.org?key=x"])
def test_verifier_rejects_invalid_base_url(url):
    with pytest.raises(ValueError):
        verify(url, "new-sha", timeout=.01)

def test_expected_version_required():
    with pytest.raises(ValueError):
        verify("http://localhost:5000", "")

def test_deploy_hook_encodes_exact_digest_without_losing_secret():
    digest = "docker.io/student/devops-mini-project@sha256:" + "a" * 64
    url = build_hook_url("https://api.render.com/deploy/srv-demo?key=test-only&imgURL=old", digest)
    query = parse_qs(urlsplit(url).query)
    assert query == {"key": ["test-only"], "imgURL": [digest]}

@pytest.mark.parametrize("hook", [
    "http://api.render.com/deploy/srv-demo?key=test",
    "https://example.org/deploy/srv-demo?key=test",
    "https://api.render.com/deploy/srv-demo",
])
def test_deploy_hook_rejects_wrong_host_or_missing_key(hook):
    with pytest.raises(ValueError):
        build_hook_url(hook, "docker.io/student/devops-mini-project@sha256:" + "a" * 64)

def test_deploy_rejects_mutable_tag():
    with pytest.raises(ValueError):
        build_hook_url("https://api.render.com/deploy/srv-demo?key=test", "docker.io/student/devops-mini-project:latest")
