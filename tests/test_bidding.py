def test_place_bid(client):
    # 1. Register seller
    res = client.post("/auth/register", json={
        "username": "seller1",
        "email": "seller@example.com",
        "password": "pass123"
    })
    assert res.status_code == 201

    # 2. Login seller
    res = client.post("/auth/login", json={
        "username": "seller1",
        "password": "pass123"
    })
    seller_token = res.get_json()["access_token"]
    seller_headers = {"Authorization": f"Bearer {seller_token}"}

    # 3. Create auction as seller
    from datetime import datetime, timedelta
    end_time = (datetime.utcnow() + timedelta(days=3)).isoformat() + "Z"
    res = client.post("/auction/create", json={
        "item_title": "Auction to Bid",
        "item_description": "Bidding test",
        "starting_bid": 50.0,
        "end_time": end_time,
        "item_condition": "New",
        "image_urls": ["http://example.com/test.png"]
    }, headers=seller_headers)
    assert res.status_code == 201
    auction_id = res.get_json()["id"]

    # 4. Register bidder
    res = client.post("/auth/register", json={
        "username": "bidder1",
        "email": "bidder@example.com",
        "password": "pass123"
    })
    assert res.status_code == 201

    # 5. Login bidder
    res = client.post("/auth/login", json={
        "username": "bidder1",
        "password": "pass123"
    })
    bidder_token = res.get_json()["access_token"]
    bidder_headers = {"Authorization": f"Bearer {bidder_token}"}

    # 6. Place bid as bidder
    res = client.post(f"/bid/place/{auction_id}",
                      json={"bid_amount": 60},
                      headers=bidder_headers)

    assert res.status_code == 200
    assert b"Bid placed successfully" in res.data
