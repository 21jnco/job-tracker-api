def test_create_job_application(client):
    client.post("/auth/register", json={
        "email": "test@gmail.com",
        "password": "zxc1234"
    })

    login_response = client.post(
        "/auth/login",
        data={
            "username": "test@gmail.com",
            "password": "zxc1234"
        }
    )

    data = login_response.json()
    token = data["access_token"]
    
    response = client.post(
        "/job-applications",
        json={
            "position": "Backend Developer",
            "company": "Google",
            "salary": 95000,
            "link": "https://github.com/21jnco"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["link"] == "https://github.com/21jnco"


def test_soft_delete(client):
    client.post("/auth/register", json={
        "email": "test@gmail.com",
        "password": "123456"
    })

    login_response = client.post("/auth/login", data={
        "username": "test@gmail.com",
        "password": "123456"
    })

    token = login_response.json()["access_token"]
    headers={"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/job-applications",
        json = {
            "position": "C++ Developer",
            "company": "Valve",
            "salary": 180000,
            "link": "https://github.com/21jnco"
        },
        headers=headers
    )

    job_application_id = create_response.json()["id"]

    delete_response = client.delete(f"/job-applications/{job_application_id}", headers=headers)

    assert delete_response.status_code == 204
    
    get_response = client.get(f"/job-applications/{job_application_id}", headers=headers)
    assert get_response.status_code == 404
