from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app, "activities", deepcopy(app.activities))
    with TestClient(app.app) as test_client:
        yield test_client


def test_root_redirects_to_homepage(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activities = deepcopy(app.activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities
    for activity in response.json().values():
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)


def test_get_activities_returns_empty_database(client, monkeypatch):
    # Arrange
    monkeypatch.setattr(app, "activities", {})

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    "method, action", [("POST", "signup"), ("DELETE", "unregister")])
def test_activity_changes_require_email(client, method, action):
    # Arrange
    endpoint = f"/activities/Chess Club/{action}"
    activities_before = deepcopy(app.activities)

    # Act
    response = client.request(method, endpoint)

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]
    assert app.activities == activities_before


def test_signup_rejects_duplicate_email(client):
    # Arrange
    email = "student@mergington.edu"
    endpoint = "/activities/Chess Club/signup"
    app.activities["Chess Club"]["participants"].append(email)
    participants_before = app.activities["Chess Club"]["participants"].copy()

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "E-mail já cadastrado na atividade"}
    assert app.activities["Chess Club"]["participants"] == participants_before


def test_signup_accepts_new_email(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert app.activities["Chess Club"]["participants"].count(email) == 1


def test_signup_allows_same_email_in_different_activity(client):
    # Arrange
    email = app.activities["Chess Club"]["participants"][0]

    # Act
    response = client.post(
        "/activities/Programming Class/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in app.activities["Programming Class"]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"
    activities_before = deepcopy(app.activities)

    # Act
    response = client.post("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert app.activities == activities_before


def test_activity_list_reflects_signup(client):
    # Arrange
    email = "student@mergington.edu"
    participants_before = app.activities["Chess Club"]["participants"].copy()

    # Act
    signup_response = client.post(
        "/activities/Chess Club/signup", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert activities_response.status_code == 200
    assert activities_response.json()["Chess Club"]["participants"] == [
        *participants_before, email]


def test_unregister_removes_only_selected_activity_signup(client):
    # Arrange
    email = app.activities["Chess Club"]["participants"][0]
    participants_before = app.activities["Chess Club"]["participants"].copy()
    app.activities["Programming Class"]["participants"].append(email)
    other_activity_before = deepcopy(app.activities["Programming Class"])

    # Act
    response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Inscrição cancelada com sucesso"}
    assert app.activities["Chess Club"]["participants"] == [
        participant for participant in participants_before if participant != email]
    assert app.activities["Programming Class"] == other_activity_before


def test_signup_allows_registration_after_unregister(client):
    # Arrange
    email = app.activities["Chess Club"]["participants"][0]
    unregister_response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email})

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert unregister_response.status_code == 200
    assert response.status_code == 200
    assert app.activities["Chess Club"]["participants"].count(email) == 1


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"
    activities_before = deepcopy(app.activities)

    # Act
    response = client.delete(
        "/activities/Unknown/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert app.activities == activities_before


def test_unregister_rejects_unknown_participant(client):
    # Arrange
    email = "unknown@mergington.edu"
    activities_before = deepcopy(app.activities)

    # Act
    response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participante não cadastrado na atividade"}
    assert app.activities == activities_before


def test_unregister_rejects_repeated_removal(client):
    # Arrange
    email = app.activities["Chess Club"]["participants"][0]
    endpoint = "/activities/Chess Club/unregister"
    first_response = client.delete(endpoint, params={"email": email})
    activities_after_first_removal = deepcopy(app.activities)

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert first_response.status_code == 200
    assert response.status_code == 404
    assert response.json() == {"detail": "Participante não cadastrado na atividade"}
    assert app.activities == activities_after_first_removal


def test_activity_list_reflects_unregister(client):
    # Arrange
    email = app.activities["Chess Club"]["participants"][0]
    expected_participants = [
        participant for participant in app.activities["Chess Club"]["participants"]
        if participant != email]

    # Act
    unregister_response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert unregister_response.status_code == 200
    assert activities_response.status_code == 200
    assert activities_response.json()["Chess Club"]["participants"] == expected_participants