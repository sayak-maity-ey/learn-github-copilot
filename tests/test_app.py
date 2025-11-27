"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create test client
client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their initial state before each test"""
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
            "description": "Join the school soccer team and compete in local leagues",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly matches",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Society": {
            "description": "Participate in acting, stage production, and school plays",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 10,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["elijah@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Clear current activities and restore original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities(self, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_structure(self, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_email(self, reset_activities):
        """Test signup fails when student already signed up"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, reset_activities):
        """Test signup fails for nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_activities(self, reset_activities):
        """Test student can sign up for multiple activities"""
        email = "teststudent@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_success(self, reset_activities):
        """Test successful unregister"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_not_signed_up(self, reset_activities):
        """Test unregister fails when student not signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, reset_activities):
        """Test unregister fails for nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_then_unregister(self, reset_activities):
        """Test signup followed by unregister"""
        email = "testuser@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]


class TestParticipantCounts:
    """Tests for participant count functionality"""
    
    def test_initial_participant_counts(self, reset_activities):
        """Test initial participant counts"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        
        programming_class = data["Programming Class"]
        assert len(programming_class["participants"]) == 2
    
    def test_participant_count_after_signup(self, reset_activities):
        """Test participant count increases after signup"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Chess Club"]["participants"])
        
        assert final_count == initial_count + 1
    
    def test_participant_count_after_unregister(self, reset_activities):
        """Test participant count decreases after unregister"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Chess Club"]["participants"])
        
        assert final_count == initial_count - 1
