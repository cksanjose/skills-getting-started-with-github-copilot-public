import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a deep copy of original activities for reset
original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    global activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert data["Basketball Team"]["description"] == "Join the basketball team and compete in local tournaments"

def test_signup_success():
    response = client.post("/activities/Basketball%20Team/signup", data={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Basketball Team" in data["message"]
    
    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball Team"]["participants"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Basketball%20Team/signup", data={"email": "test@example.com"})
    
    # Second signup
    response = client.post("/activities/Basketball%20Team/signup", data={"email": "test@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_invalid_activity():
    response = client.post("/activities/Invalid%20Activity/signup", data={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Basketball%20Team/signup", data={"email": "test@example.com"})
    
    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister", data={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered test@example.com from Basketball Team" in data["message"]
    
    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" not in data["Basketball Team"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Basketball%20Team/unregister", data={"email": "test@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "Student is not signed up" in data["detail"]

def test_unregister_invalid_activity():
    response = client.delete("/activities/Invalid%20Activity/unregister", data={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]