def test_register_and_login(client):
    # Register a user
    res = client.post("/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "pass123"
    })
    assert res.status_code == 201

    # Login
    res = client.post("/auth/login", json={
        "username": "user1",
        "password": "pass123"
    })
    data = res.get_json()
    assert res.status_code == 200
    assert "access_token" in data
