def test_register_user(client):
    response = client.post("/auth/register", json={
        "email": "test@gmail.com",
        "password": "zxc1234"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@gmail.com"


def test_login_user(client):
    client.post("/auth/register", json={
        "email": "test@gmail.com",
        "password": "zxc1234"
    })

    response = client.post(
        "/auth/login",
        data={
            "username": "test@gmail.com",
            "password": "zxc1234"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] is not None
