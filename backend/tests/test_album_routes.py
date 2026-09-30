def test_create_album(client):
    response = client.post(
        "/api/v1/albums",
        json={
            "title": "Test Album",
            "artist_id": 1,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == "Test Album"
    assert body["artist_id"] == 1
    assert "id" in body
