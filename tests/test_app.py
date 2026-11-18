"""
Test suite for Mergington High School API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a TestClient instance for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities to initial state before each test"""
    from src.app import activities
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in team games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Track and Field": {
            "description": "Train for running, jumping, and throwing events",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Club": {
            "description": "Explore drawing, painting, and other visual art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Drama Club": {
            "description": "Develop acting skills and create theatrical productions",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Build public speaking skills and debate current topics",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Explore scientific ideas through experiments and projects",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": []
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(original_activities)


# ============================================================================
# GET / Tests
# ============================================================================

def test_root_redirects_to_static_index(client):
    """Test that GET / redirects to /static/index.html"""
    # Arrange
    # (No setup needed for redirect test)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ============================================================================
# GET /activities Tests
# ============================================================================

def test_get_activities_returns_all_activities(client, reset_activities):
    """Test that GET /activities returns all activities"""
    # Arrange
    expected_activity_count = 9
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert response.status_code == 200
    assert len(activities) == expected_activity_count
    assert "Chess Club" in activities
    assert "Programming Class" in activities


def test_get_activities_has_correct_structure(client, reset_activities):
    """Test that activity objects have the correct structure"""
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert response.status_code == 200
    for activity_name, activity_data in activities.items():
        assert set(activity_data.keys()) == required_fields
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["max_participants"], int)


def test_get_activities_contains_initial_participants(client, reset_activities):
    """Test that activities contain expected initial participants"""
    # Arrange
    expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert response.status_code == 200
    assert activities["Chess Club"]["participants"] == expected_chess_participants


# ============================================================================
# POST /signup Tests
# ============================================================================

def test_signup_successful(client, reset_activities):
    """Test successful student signup for an activity"""
    # Arrange
    activity_name = "Basketball Team"
    email = "new_student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_adds_email_to_participants(client, reset_activities):
    """Test that signup actually adds the email to activity participants"""
    # Arrange
    activity_name = "Basketball Team"
    email = "new_student@mergington.edu"
    
    # Act - Sign up
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Act - Retrieve updated activities
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client, reset_activities):
    """Test signup fails when activity does not exist"""
    # Arrange
    activity_name = "NonexistentActivity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_signed_up(client, reset_activities):
    """Test signup fails when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already a participant
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# ============================================================================
# POST /remove Tests
# ============================================================================

def test_remove_successful(client, reset_activities):
    """Test successful removal of a student from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_remove_deletes_email_from_participants(client, reset_activities):
    """Test that remove actually deletes the email from activity participants"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act - Remove student
    client.post(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    
    # Act - Retrieve updated activities
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert email not in activities[activity_name]["participants"]


def test_remove_activity_not_found(client, reset_activities):
    """Test remove fails when activity does not exist"""
    # Arrange
    activity_name = "NonexistentActivity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_not_found(client, reset_activities):
    """Test remove fails when participant is not in the activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "not_a_participant@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
