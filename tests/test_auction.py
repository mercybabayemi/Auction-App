from datetime import datetime,timedelta
def test_create_and_list_auctions(client):
    # 1. Register user
    res = client.post("/auth/register", json={
        "username": "auction_owner",
        "email": "owner@example.com",
        "password": "pass123"
    })
    assert res.status_code == 201

    # 2. Login user to get access token
    res = client.post("/auth/login", json={
        "username": "auction_owner",
        "password": "pass123"
    })
    assert res.status_code == 200
    print("Login response JSON:", res.get_json())
    token = res.get_json()["access_token"]


    headers = {"Authorization": f"Bearer {token}"}
    print("Using headers:", headers)

    # Prepare end_time: 1 day in the future
    end_time = (datetime.utcnow() + timedelta(days=3)).isoformat() + "Z"

    # 3. Create auction
    res = client.post("/auction/create", json={
        "item_title": "Test Auction",
        "item_description": "A simple test auction",
        "starting_bid": 100.0,
        "end_time": end_time,
        "item_condition": "New",
        "image_urls": ["http://example.com/image.png"]
    }, headers=headers)
    assert res.status_code == 201

    # 4. List auctions
    res = client.get("/auction/", headers={"Accept": "application/json"})
    print("Auction list raw response:", res.data)
    print("Auction list headers:", res.headers)
    assert res.status_code == 200
    data = res.get_json()
    print("Auction list response:", data)
    assert any(auction["item_title"] == "Test Auction" for auction in data)