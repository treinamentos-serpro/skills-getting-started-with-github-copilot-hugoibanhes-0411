from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app, "activities", deepcopy(app.activities))
    with TestClient(app.app) as test_client:
        yield test_client


def test_signup_rejects_duplicate_email(client):
    email = "student@mergington.edu"
    endpoint = "/activities/Chess Club/signup"
    assert client.post(endpoint, params={"email": email}).status_code == 200
    participants_before = app.activities["Chess Club"]["participants"].copy()

    response = client.post(endpoint, params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "E-mail já cadastrado na atividade"}
    assert app.activities["Chess Club"]["participants"] == participants_before


def test_signup_accepts_new_email(client):
    email = "student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert app.activities["Chess Club"]["participants"].count(email) == 1


def test_signup_allows_same_email_in_different_activity(client):
    email = app.activities["Chess Club"]["participants"][0]

    response = client.post(
        "/activities/Programming Class/signup", params={"email": email})

    assert response.status_code == 200
    assert email in app.activities["Programming Class"]["participants"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}