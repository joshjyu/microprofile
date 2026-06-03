from httpx import AsyncClient


async def test_create_profile_returns_id(client: AsyncClient) -> None:
    """
    Assert POST /profiles returns 201 with a unique ID.

    Parameters:
      client: Async test client with mock database.
    """
    response = await client.post(
        "/profiles", json={"username": "testuser", "password": "secret"}
    )
    assert response.status_code == 201
    assert "id" in response.json()


async def test_create_profile_rejects_duplicate_username(
    client: AsyncClient,
) -> None:
    """
    Assert POST /profiles returns 409 when username already exists.

    Parameters:
      client: Async test client with mock database.
    """
    payload = {"username": "dupuser", "password": "secret"}
    await client.post("/profiles", json=payload)
    response = await client.post("/profiles", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already taken"


async def test_get_profile_returns_profile(client: AsyncClient) -> None:
    """
    Assert GET /profiles/{user_id} returns 200 with correct profile data.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "getuser", "password": "secret"},
    )
    user_id = create.json()["id"]
    response = await client.get(f"/profiles/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "getuser"
    assert "created_at" in data


async def test_get_profile_returns_404_for_invalid_user(
    client: AsyncClient,
) -> None:
    """
    Assert GET /profiles/{user_id} returns 404 for unknown user.

    Parameters:
      client: Async test client with mock database.
    """
    response = await client.get("/profiles/000000000000000000000000")
    assert response.status_code == 404


async def test_get_app_data_returns_stored_data(
    client: AsyncClient,
) -> None:
    """
    Assert GET /profiles/{user_id}/apps/{app_id} returns stored data.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "appdatauser", "password": "secret"},
    )
    user_id = create.json()["id"]
    payload = {"score": 42, "level": 3}
    await client.put(f"/profiles/{user_id}/apps/mygame", json=payload)
    response = await client.get(f"/profiles/{user_id}/apps/mygame")
    assert response.status_code == 200
    assert response.json() == payload


async def test_get_app_data_returns_404_for_missing_app(
    client: AsyncClient,
) -> None:
    """
    Assert GET /profiles/{user_id}/apps/{app_id} returns 404 when no data stored.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "noappdatauser", "password": "secret"},
    )
    user_id = create.json()["id"]
    response = await client.get(f"/profiles/{user_id}/apps/mygame")
    assert response.status_code == 404


async def test_update_app_data_sets_data(client: AsyncClient) -> None:
    """
    Assert PUT /profiles/{user_id}/apps/{app_id} returns 200.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles", json={"username": "appuser", "password": "secret"}
    )
    user_id = create.json()["id"]
    response = await client.put(
        f"/profiles/{user_id}/apps/myapp", json={"score": 42, "level": 3}
    )
    assert response.status_code == 200


async def test_update_app_data_returns_404_for_invalid_user(
    client: AsyncClient,
) -> None:
    """
    Assert PUT /profiles/{user_id}/apps/{app_id} returns 404 for unknown user.

    Parameters:
      client: Async test client with mock database.
    """
    response = await client.put(
        "/profiles/000000000000000000000000/apps/myapp",
        json={"score": 42},
    )
    assert response.status_code == 404


async def test_patch_profile_updates_username(client: AsyncClient) -> None:
    """
    Assert PATCH /profiles/{user_id} returns 200 on valid username update.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "patchuser", "password": "secret"},
    )
    user_id = create.json()["id"]
    response = await client.patch(
        f"/profiles/{user_id}",
        json={"username": "patchuser_updated"},
    )
    assert response.status_code == 200


async def test_patch_profile_rejects_duplicate_username(
    client: AsyncClient,
) -> None:
    """
    Assert PATCH /profiles/{user_id} returns 409 when username is taken.

    Parameters:
      client: Async test client with mock database.
    """
    await client.post(
        "/profiles", json={"username": "existing", "password": "secret"}
    )
    create = await client.post(
        "/profiles", json={"username": "patchuser2", "password": "secret"}
    )
    user_id = create.json()["id"]
    response = await client.patch(
        f"/profiles/{user_id}", json={"username": "existing"}
    )
    assert response.status_code == 409


async def test_patch_profile_allows_same_username(
    client: AsyncClient,
) -> None:
    """
    Assert PATCH /profiles/{user_id} returns 200 when username is unchanged.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles", json={"username": "sameuser", "password": "secret"}
    )
    user_id = create.json()["id"]
    response = await client.patch(
        f"/profiles/{user_id}", json={"username": "sameuser"}
    )
    assert response.status_code == 200


async def test_patch_profile_returns_404_for_invalid_user(
    client: AsyncClient,
) -> None:
    """
    Assert PATCH /profiles/{user_id} returns 404 for unknown user.

    Parameters:
      client: Async test client with mock database.
    """
    response = await client.patch(
        "/profiles/000000000000000000000000",
        json={"username": "ghost"},
    )
    assert response.status_code == 404


async def test_patch_profile_updates_password(client: AsyncClient) -> None:
    """
    Assert PATCH /profiles/{user_id} returns 200 on valid password update.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "passuser", "password": "oldpassword"},
    )
    user_id = create.json()["id"]
    response = await client.patch(
        f"/profiles/{user_id}",
        json={"password": "newpassword"},
    )
    assert response.status_code == 200


async def test_patch_profile_updates_both_fields(
    client: AsyncClient,
) -> None:
    """
    Assert PATCH /profiles/{user_id} returns 200 when updating both fields.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "bothuser", "password": "oldpassword"},
    )
    user_id = create.json()["id"]
    response = await client.patch(
        f"/profiles/{user_id}",
        json={"username": "bothuser_new", "password": "newpassword"},
    )
    assert response.status_code == 200


async def test_patch_profile_returns_400_for_empty_body(
    client: AsyncClient,
) -> None:
    """
    Assert PATCH /profiles/{user_id} returns 400 when no fields are provided.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "emptyuser", "password": "secret"},
    )
    user_id = create.json()["id"]
    response = await client.patch(
        f"/profiles/{user_id}",
        json={},
    )
    assert response.status_code == 400


async def test_delete_profile_removes_user(client: AsyncClient) -> None:
    """
    Assert DELETE /profiles/{user_id} returns 200 for an existing user.

    Parameters:
      client: Async test client with mock database.
    """
    create = await client.post(
        "/profiles",
        json={"username": "deleteuser", "password": "secret"},
    )
    user_id = create.json()["id"]
    response = await client.delete(f"/profiles/{user_id}")
    assert response.status_code == 200


async def test_delete_profile_invalid_user(
    client: AsyncClient,
) -> None:
    """
    Assert DELETE /profiles/{user_id} returns 404 for unknown user.

    Parameters:
      client: Async test client with mock database.
    """
    response = await client.delete("/profiles/000000000000000000000000")
    assert response.status_code == 404
