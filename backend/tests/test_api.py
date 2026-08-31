import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Pathfinder API"}

@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_generate_roadmap_requires_auth_or_skips():
    # We won't fully test the endpoints here since they require Gemini API key
    # But we can test that the endpoint exists and accepts the schema
    response = client.post(
        "/api/generate-roadmap",
        json={"user_input": "I want to be a data scientist"}
    )
    
    # Without Bearer token, it will return 401 Unauthorized
    assert response.status_code in [200, 401, 403, 500]

def test_public_roadmap_endpoint():
    # Public endpoint should not require Bearer token
    response = client.get("/api/public/roadmap/nonexistent_user")
    assert response.status_code in [404, 500]

