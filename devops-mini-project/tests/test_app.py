import pytest
from app import create_app

@pytest.fixture
def client():
    return create_app({"TESTING": True, "APP_VERSION": "commit-123"}).test_client()

def test_home_contains_report_messages_and_names(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for text in ["Hello from", "DevOps!", "CI/CD Pipeline Working Successfully!",
                 "Aayush Patil (84)", "Sanskruti Suryawanshi (56)", "Ms. Kshitija Gharat"]:
        assert text in html

def test_health_exposes_expected_release_and_is_not_cached(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["version"] == "commit-123"
    assert "no-store" in response.headers["Cache-Control"]
    assert response.json["time_utc"].endswith("+00:00")

def test_unknown_route_is_404(client):
    response = client.get("/missing")
    assert response.status_code == 404
    assert "Back to the application" in response.get_data(as_text=True)

@pytest.mark.parametrize("path", ["/", "/health"])
def test_post_not_allowed(client, path):
    assert client.post(path).status_code == 405

@pytest.mark.parametrize("path", ["/static/style.css", "/static/app.js"])
def test_required_assets_are_served(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert len(response.data) > 100

def test_html_escapes_release_metadata():
    client = create_app({"TESTING": True, "APP_VERSION": "<script>alert(1)</script>"}).test_client()
    html = client.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html

def test_environment_release_is_loaded(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "from-environment")
    assert create_app().test_client().get("/health").json["version"] == "from-environment"

def test_response_security_headers(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
