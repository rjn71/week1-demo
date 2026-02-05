"""
Test suite for Mergington High School API endpoints

This test suite covers all API endpoints for the high school activities management system,
including activity retrieval, student signup, and participant removal functionality.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Create a test client for the API.
    
    This fixture provides a TestClient instance that can make HTTP requests
    to the FastAPI application without needing to run an actual server.
    It's used by all test methods to interact with the API endpoints.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities data before and after each test.
    
    This fixture runs automatically (autouse=True) before each test to ensure
    test isolation. It resets the in-memory activities database to a known state,
    preventing tests from interfering with each other. Without this, one test's
    modifications (adding/removing participants) would affect subsequent tests.
    """
    # Store original state with all default activities and participants
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
        "Soccer Team": {
            "description": "Join our varsity soccer team and compete in regional tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "ryan@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve your swimming technique and participate in swim meets",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lily@mergington.edu", "grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and theatrical performances throughout the year",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 24,
            "participants": ["ethan@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills through competitive debates",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "mia@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots for competitions",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    yield
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Test that duplicate signup is rejected"""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test.user%2Btest@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First, add a student
        client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Chess%20Club/participants/test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unregistered" in data["message"].lower()
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_with_url_encoded_email(self, client):
        """Test unregistering with URL-encoded email"""
        # Add participant with special characters
        client.post("/activities/Chess%20Club/signup?email=test%2Buser@mergington.edu")
        
        # Unregister with URL encoding
        response = client.delete(
            "/activities/Chess%20Club/participants/test%2Buser@mergington.edu"
        )
        assert response.status_code == 200


class TestActivityWorkflow:
    """Integration tests for complete activity workflows"""
    
    def test_complete_signup_and_unregister_workflow(self, client):
        """Test a complete workflow: signup, verify, unregister, verify"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Signup
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert email in after_signup.json()[activity]["participants"]
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants/{email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        after_unregister = client.get("/activities")
        assert email not in after_unregister.json()[activity]["participants"]
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
    
    def test_multiple_signups_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multi@mergington.edu"
        
        # Signup for multiple activities
        client.post("/activities/Chess%20Club/signup?email=" + email)
        client.post("/activities/Programming%20Class/signup?email=" + email)
        client.post("/activities/Gym%20Class/signup?email=" + email)
        
        # Verify all signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]
        assert email in data["Gym Class"]["participants"]
