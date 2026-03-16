import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root URL redirects to static index.html"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    # FastAPI redirects internally, but since static files are mounted,
    # it should serve the HTML file

def test_get_activities():
    """Test getting all activities"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check structure of first activity
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    
    # Additional assertion - verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test that duplicate signup is prevented"""
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    
    # Act - First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act - Second signup (the actual test action)
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_invalid_activity():
    """Test signup for non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    
    # Act
    response = client.post(f"/activities/NonExistent/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_success():
    """Test successful unregistration from an activity"""
    # Arrange
    activity_name = "Programming Class"
    email = "unregister@mergington.edu"
    
    # Act - First sign up
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act - Then unregister (the actual test action)
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "Unregistered" in result["message"]
    
    # Additional assertion - verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_signed_up():
    """Test unregistering a student who isn't signed up"""
    # Arrange
    activity_name = "Gym Class"
    email = "notsignedup@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not signed up" in result["detail"]

def test_unregister_invalid_activity():
    """Test unregistering from non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/NonExistent/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]