def test_signup_and_login(client, db_session):
    # signup
    payload = {"email": "testuser@example.com", "password": "TestPass123!", "full_name": "Test User"}
    r = client.post("/auth/signup", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == payload["email"]

    # login
    r2 = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    token_data = r2.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
