"""
Pytest configuration and shared fixtures for the FastAPI test suite.

This module provides fixtures for testing the Mergington High School Activities API,
including TestClient setup and activity state management.
"""

import pytest
import importlib
import copy
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for making HTTP requests to the FastAPI app.
    
    Uses dynamic module loading to ensure app is properly initialized.
    """
    # ARRANGE - Load the app module dynamically
    app_module = importlib.import_module("src.app")
    app = app_module.app
    
    # ACT - Create and return TestClient
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture that provides the initial activities data structure.
    
    Returns a deep copy to prevent test state leakage.
    """
    activities_data = {
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
            "description": "Practice teamwork and compete in local soccer matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Develop basketball skills and play in league games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Volleyball Team": {
            "description": "Build teamwork and improve serving, passing, and defense skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": []
        },
        "Track and Field": {
            "description": "Train for running, jumping, and relay events throughout the season",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore drawing, painting, and creative projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ella@mergington.edu", "grace@mergington.edu"]
        },
        "Photography Club": {
            "description": "Learn composition, editing, and storytelling through photography",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Drama Club": {
            "description": "Act, direct, and produce school theater performances",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "charlotte@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Practice ensemble performance and grow your musical skills",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Math Olympiad": {
            "description": "Solve advanced problems and compete in math contests",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Debate Team": {
            "description": "Develop argumentation, speaking, and critical thinking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        }
    }
    return copy.deepcopy(activities_data)


@pytest.fixture(autouse=True)
def reset_activities(client, sample_activities):
    """
    Autouse fixture that resets the activities data before each test.
    
    This ensures test isolation - each test starts with a clean state.
    """
    # ARRANGE - Get access to the app module and activities dict
    app_module = importlib.import_module("src.app")
    
    # Clear and reset the activities dictionary to initial state
    app_module.activities.clear()
    app_module.activities.update(sample_activities)
    
    # Yield to run the test
    yield
    
    # Cleanup: Reset again after test completes (though usually not necessary)
    app_module.activities.clear()
    app_module.activities.update(sample_activities)
