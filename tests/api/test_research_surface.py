from fastapi.testclient import TestClient

from apps.api.main import app


def test_research_api_surface_is_exposed():
    route_paths = {route.path for route in app.routes}

    expected_paths = {
        "/vaults/",
        "/vaults/secrets",
        "/context/verify",
        "/context/zk/generate",
        "/trust/evaluate",
        "/access/evaluate",
        "/access/request-secret",
        "/access/events",
        "/memory/index/local-folder",
        "/memory/query",
        "/agents/register",
        "/agents/decision",
        "/audit/",
        "/zk/verify-context",
        "/zk/vault-access",
        "/auth/token",
    }

    assert expected_paths.issubset(route_paths)


def test_root_describes_research_system():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "reliquary-api"
    assert "research_surfaces" in body
    assert {"vaults", "context", "trust", "access", "memory", "agents", "audit", "auth"}.issubset(
        body["research_surfaces"]
    )
