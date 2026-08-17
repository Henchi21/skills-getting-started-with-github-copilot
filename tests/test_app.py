"""
Comprehensive test suite for the FastAPI Mergington High School Activities API.

Tests use the AAA (Arrange-Act-Assert) pattern and are organized by feature:
- TestRedirect: Tests for the root redirect endpoint
- TestGetActivities: Tests for listing all activities
- TestSignup: Tests for signing up for activities
- TestUnregister: Tests for unregistering from activities
"""

import pytest
import importlib
from fastapi.testclient import TestClient


class TestRedirect:
    """Tests for GET / redirect endpoint."""

    def test_root_redirect_returns_307(self, client):
        """
        ARRANGE: No setup needed for root redirect
        ACT: Send GET request to root
        ASSERT: Should redirect with 307 status code
        """
        # ACT
        response = client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_location_is_correct(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to root with follow_redirects=True
        ASSERT: Should end up at /static/index.html
        """
        # ACT
        response = client.get("/", follow_redirects=True)
        
        # ASSERT
        assert response.status_code == 200
        # Verify we can access the HTML file
        assert "<html" in response.text.lower() or "mergington" in response.text.lower()


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """
        ARRANGE: No setup needed - activities are pre-loaded
        ACT: Send GET request to /activities
        ASSERT: Should return 200 status code
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200

    def test_get_activities_returns_json(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request to /activities
        ASSERT: Response should be valid JSON
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_includes_all_activities(self, client):
        """
        ARRANGE: No setup needed - 13 activities are pre-loaded
        ACT: Send GET request to /activities
        ASSERT: Should include all 13 activities
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Team", "Volleyball Team", "Track and Field", "Art Club",
            "Photography Club", "Drama Club", "Music Ensemble", "Math Olympiad",
            "Debate Team"
        }
        assert set(data.keys()) == expected_activities

    def test_get_activities_has_required_fields(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request and check first activity
        ASSERT: Each activity should have required fields
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # ASSERT
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_is_list(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request and inspect participants field
        ASSERT: Participants should be a list
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_max_participants_is_integer(self, client):
        """
        ARRANGE: No setup needed
        ACT: Send GET request and inspect max_participants field
        ASSERT: max_participants should be an integer
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details["max_participants"], int)
            assert activity_details["max_participants"] > 0


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_with_query_param(self, client):
        """
        ARRANGE: Prepare activity name and new email
        ACT: Send POST signup request
        ASSERT: Should return 200 and success message
        """
        # ARRANGE
        activity_name = "Volleyball Team"
        email = "newstudent@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "signed up" in data["message"].lower()
        assert email in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        ARRANGE: Prepare to signup a student
        ACT: Sign up and verify participant list
        ASSERT: New participant should be in the activity
        """
        # ARRANGE
        activity_name = "Track and Field"
        email = "sprinter@mergington.edu"
        
        # ACT
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert email in data[activity_name]["participants"]

    def test_signup_activity_not_found_returns_404(self, client):
        """
        ARRANGE: Use non-existent activity name
        ACT: Try to sign up for non-existent activity
        ASSERT: Should return 404 error
        """
        # ARRANGE
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_missing_email_returns_400(self, client):
        """
        ARRANGE: Activity exists but no email provided
        ACT: Send signup request without email
        ASSERT: Should return 400 error
        """
        # ARRANGE
        activity_name = "Photography Club"
        
        # ACT
        response = client.post(f"/activities/{activity_name}/signup")
        
        # ASSERT
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_signup_duplicate_signup_returns_400(self, client):
        """
        ARRANGE: Sign up a student once successfully
        ACT: Try to sign up the same student again
        ASSERT: Should return 400 error
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_signup_at_capacity_returns_400(self, client):
        """
        ARRANGE: Get an activity and fill it to capacity
        ACT: Try to add another participant when full
        ASSERT: Should return 400 error
        """
        # ARRANGE - Find or create a small activity
        app_module = importlib.import_module("src.app")
        
        # Use Photography Club with max 12, currently 0
        activity_name = "Photography Club"
        app_module.activities[activity_name]["max_participants"] = 1
        app_module.activities[activity_name]["participants"] = ["existing@mergington.edu"]
        
        email = "newstudent@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_increments_participant_count(self, client):
        """
        ARRANGE: Get initial participant count
        ACT: Sign up a new student
        ASSERT: Participant count should increase by 1
        """
        # ARRANGE
        activity_name = "Volleyball Team"
        email = "newvolleyball@mergington.edu"
        
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        # ACT
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        assert count_after == count_before + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """
        ARRANGE: Prepare registered activity and participant
        ACT: Send DELETE unregister request
        ASSERT: Should return 200 and success message
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unregistered" in data["message"].lower()

    def test_unregister_removes_participant(self, client):
        """
        ARRANGE: Get a registered participant
        ACT: Unregister the participant
        ASSERT: Participant should no longer be in the activity
        """
        # ARRANGE
        activity_name = "Drama Club"
        email = "lucas@mergington.edu"
        
        # ACT
        client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert email not in data[activity_name]["participants"]

    def test_unregister_activity_not_found_returns_404(self, client):
        """
        ARRANGE: Use non-existent activity
        ACT: Try to unregister from non-existent activity
        ASSERT: Should return 404 error
        """
        # ARRANGE
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_missing_email_returns_400(self, client):
        """
        ARRANGE: Activity exists but no email provided
        ACT: Send unregister request without email
        ASSERT: Should return 422 validation error
        """
        # ARRANGE
        activity_name = "Art Club"
        
        # ACT
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        # ASSERT
        assert response.status_code == 422
        detail_list = response.json()["detail"]
        assert isinstance(detail_list, list)
        assert "email" in detail_list[0]["loc"]

    def test_unregister_not_registered_returns_400(self, client):
        """
        ARRANGE: Use email not registered for activity
        ACT: Try to unregister someone not signed up
        ASSERT: Should return 400 error
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_decrements_participant_count(self, client):
        """
        ARRANGE: Get initial participant count
        ACT: Unregister a participant
        ASSERT: Participant count should decrease by 1
        """
        # ARRANGE
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        # ACT
        client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # ASSERT
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        assert count_after == count_before - 1


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_signup_then_unregister_roundtrip(self, client):
        """
        ARRANGE: Prepare a new participant
        ACT: Sign up, verify, then unregister
        ASSERT: Participant should be gone after unregister
        """
        # ARRANGE
        activity_name = "Music Ensemble"
        email = "musician@mergington.edu"
        
        # ACT - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        check_response = client.get("/activities")
        assert email in check_response.json()[activity_name]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # ASSERT - Verify unregistered
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity_name]["participants"]

    def test_multiple_participants_signup_and_unregister(self, client):
        """
        ARRANGE: Multiple different participants
        ACT: Sign up multiple participants and unregister some
        ASSERT: Correct participants remain in activity
        """
        # ARRANGE
        activity_name = "Math Olympiad"
        emails = ["math1@mergington.edu", "math2@mergington.edu", "math3@mergington.edu"]
        
        # ACT - Sign up all
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify all signed up
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in emails:
            assert email in participants
        
        # Unregister one
        client.delete(
            f"/activities/{activity_name}/unregister?email={emails[1]}"
        )
        
        # ASSERT - Verify correct participant removed
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert emails[0] in final_participants
        assert emails[1] not in final_participants
        assert emails[2] in final_participants
