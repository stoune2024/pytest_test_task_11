import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_create_user_success(user_public):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {"username": "johndoe", "password": "deadpond"}
        data.update(user_public)
        response = await ac.post("/user/", data=data)
    assert response.status_code == 200
    assert "created_user" in response.json()
    async with AsyncClient( # Удаляем созданного пользователя во избежание ошибок
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        await ac.delete("/users/1")


@pytest.mark.asyncio
async def test_create_user_no_username_passed(user_public):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {"password": "deadpond"}
        data.update(user_public)
        response = await ac.post("/user/", data=data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "username"],
                "msg": "Field required",
                "input": {
                    "id": "1",
                    "name": "John",
                    "age": "35",
                    "email": "johndoe@mail.com",
                    "password": "deadpond",
                    "is_supervisor": "true",
                    "phone_number": "+8 (800) 555-35-35",
                },
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_user_no_data_passed():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        response = await ac.post("/user/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_users_success(list_of_user_create):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        response = await ac.post("/users/", json=list_of_user_create)
    assert response.status_code == 200
    assert "users_created" in response.json()
    for i in range(5):
        async with AsyncClient(  # Удаляем пользователей
                transport=ASGITransport(app=app), base_url="http://test/user"
        ) as ac:
            await ac.delete(f"/users/{i}")


@pytest.mark.asyncio
async def test_create_users_no_data_passed():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        response = await ac.post("/users/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_user_success(user_public, mocker):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {"username": "johndoe", "password": "deadpond"}
        data.update(user_public)
        await ac.post("/user/", data=data)
    mocker.patch(
        "apps.user.routers.jwt.decode",
        return_value={"sub": "username", "type": "bearer"},
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/protected_user"
    ) as ac:
        get_response = await ac.get("/users/1")
    assert get_response.status_code == 200
    assert get_response.json() == {
        "id": 1,
        "name": "John",
        "age": 35,
        "isSupervisor": True,
        "email": "johndoe@mail.com",
        "phoneNumber": "+8 (800) 555-35-35",
    }
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test/protected_user"
    ) as ac:
        await ac.delete(f"/users/1")


@pytest.mark.asyncio
async def test_read_user_no_user_found(user_public, mocker):
    mocker.patch(
        "apps.user.routers.jwt.decode",
        return_value={"sub": "username", "type": "bearer"},
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/protected_user"
    ) as ac:
        response = await ac.get("/users/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": None,
        "name": None,
        "age": None,
        "isSupervisor": None,
        "email": None,
        "phoneNumber": None,
    }


@pytest.mark.asyncio
async def test_read_users_list_success(list_of_user_create):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        await ac.post("/users/", json=list_of_user_create)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        response = await ac.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 5
    for i in range(5):
        async with AsyncClient(  # Удаляем пользователей
                transport=ASGITransport(app=app), base_url="http://test/user"
        ) as ac:
            await ac.delete(f"/users/{i}")



@pytest.mark.asyncio
async def test_read_users_list_no_users_found():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        response = await ac.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_users_list_wrong_query(list_of_user_create):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        await ac.post("/users/", json=list_of_user_create)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        response = await ac.get("/users/?start_index=-2")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "greater_than_equal",
                "loc": ["query", "start_index"],
                "msg": "Input should be greater than or equal to 0",
                "input": "-2",
                "ctx": {"ge": 0},
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_user_success(user_public):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {"username": "johndoe", "password": "deadpond"}
        data.update(user_public)
        await ac.post("/user/", data=data)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {
            "username": "johndoe",
            "password": "deadpond",
            "id": 1,
            "name": "Smith",
            "age": 25,
            "is_supervisor": True,
            "email": "johndoe@mail.com",
            "phone_number": "+8 (800) 555-35-35",
        }

        patch_response = await ac.patch("/users/1", data=data)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        get_response = await ac.get("/users/")
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Smith"
    assert get_response.status_code == 200
    assert get_response.json()[0]["name"] == "Smith"
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        await ac.delete(f"/users/1")


@pytest.mark.asyncio
async def test_update_user_no_user_found(user_public):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {
            "username": "johndoe",
            "password": "deadpond",
            "id": 1,
            "name": "Smith",
            "age": 25,
            "is_supervisor": True,
            "email": "johndoe@mail.com",
            "phone_number": "+8 (800) 555-35-35",
        }

        patch_response = await ac.patch("/users/1", data=data)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        get_response = await ac.get("/users/")
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == None
    assert patch_response.json()["email"] == None
    assert get_response.status_code == 200
    assert get_response.json() == []


@pytest.mark.asyncio
async def test_update_user_data_passed_is_invalid(user_public):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {"username": "johndoe", "password": "deadpond"}
        data.update(user_public)
        await ac.post("/user/", data=data)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {
            "id": 1,
            "name": "Smith",
            "age": 25,
            "is_supervisor": True,
            "email": "johndoe@mail.com",
            "phone_number": "+8 (800) 555-35-35",
        }

        patch_response = await ac.patch("/users/1", data=data)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        get_response = await ac.get("/users/")
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == None
    assert patch_response.json()["email"] == None
    assert get_response.status_code == 200
    assert get_response.json()[0] == {
        "age": 35,
        "email": "johndoe@mail.com",
        "id": 1,
        "isSupervisor": True,
        "name": "John",
        "phoneNumber": "+8 (800) 555-35-35",
    }
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        await ac.delete(f"/users/1")


@pytest.mark.asyncio
async def test_delete_user_success(user_public):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        data = {"username": "johndoe", "password": "deadpond"}
        data.update(user_public)
        await ac.post("/user/", data=data)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        response = await ac.delete("/users/1")

    assert response.status_code == 200
    assert response.json() == {
        "message": "User with ID: 1 has been deleted succesfully"
    }


@pytest.mark.asyncio
async def test_delete_user_no_user_found(user_public):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        delete_response = await ac.delete("/users/10")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/user"
    ) as ac:
        get_response = await ac.get("/users/")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "User with ID: 10 has been deleted succesfully"
    }
    assert get_response.status_code == 200
    assert get_response.json() == []
