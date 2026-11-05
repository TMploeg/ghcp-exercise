import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays",
            "max_participants": 5,
            "participants": [
                "existing@mergington.edu",
                "remove@mergington.edu",
                "remove@mergington.edu",
            ],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == app_module.activities


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@mergington.edu for Chess Club"
    }
    assert "new@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    participants_before = app_module.activities["Chess Club"]["participants"].copy()

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert app_module.activities["Chess Club"]["participants"] == participants_before


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_and_duplicates(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "remove@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered remove@mergington.edu from Chess Club"
    }
    assert app_module.activities["Chess Club"]["participants"] == [
        "existing@mergington.edu"
    ]


def test_unregister_returns_not_found_for_unregistered_participant(client):
    participants_before = app_module.activities["Chess Club"]["participants"].copy()

    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert app_module.activities["Chess Club"]["participants"] == participants_before


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"