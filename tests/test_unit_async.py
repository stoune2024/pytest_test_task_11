from datetime import timedelta
import asyncio
from starlette.requests import Request
from starlette.responses import Response

from apps.auth.services import (
    get_user,
    authenticate_user,
    create_access_token,
    verify_token,
)
from apps.user.routers import check_if_user_authorized
from apps.external_API.services import fetch_data
from fastapi import HTTPException
import pytest
from pytest import mark


@mark.services
@mark.database
@pytest.mark.asyncio
async def test_get_user_success(mocker, connection):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe"},
    )
    result = await get_user("johndoe", connection)
    assert result == {"id": 1, "username": "johndoe"}


@mark.services
@mark.database
@pytest.mark.asyncio
async def test_get_user_not_found(mocker):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe"},
    )
    with pytest.raises(HTTPException, match="Пользователь не найден"):
        await get_user("johndoe", "connection")


@mark.services
@mark.database
@pytest.mark.asyncio
async def test_authenticate_user_success(mocker, connection):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe", "hashed_password": "johncoffee"},
    )
    mocker.patch("apps.auth.services.CryptContext.verify", return_value=True)
    result = await authenticate_user("username", "johncoffee", connection)
    assert result == {"id": 1, "username": "johndoe", "hashed_password": "johncoffee"}


@mark.services
@mark.database
@pytest.mark.asyncio
async def test_authenticate_user_not_found(mocker):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe", "hashed_password": "johncoffee"},
    )
    with pytest.raises(HTTPException, match="Пользователь не найден"):
        await authenticate_user("username", "johncoffee", "connection")


@mark.services
@mark.database
@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(mocker, connection):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe", "hashed_password": "johncoffee"},
    )
    mocker.patch("apps.auth.services.CryptContext.verify", return_value=False)
    with pytest.raises(HTTPException, match="Введен неверный пароль"):
        await authenticate_user("username", "johncoffee", connection)


@mark.services
@pytest.mark.asyncio
async def test_create_access_token(mocker, settings):
    mocker.patch("apps.auth.services.jwt.encode", return_value="encoded_jwt_token")
    result = await create_access_token(
        settings,
        {"sub": "johndoe"},
        timedelta(days=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    assert result == "encoded_jwt_token"


@mark.services
@pytest.mark.asyncio
async def test_verify_token_success(mocker, settings, connection):
    mocker.patch(
        "apps.auth.services.jwt.decode",
        return_value={"sub": "johndoe", "type": "bearer"},
    )
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe", "hashed_password": "johncoffee"},
    )
    result = await verify_token(
        settings, "extra_secret_jwt_token", "request", connection
    )
    assert result.username == "johndoe"


@mark.services
@pytest.mark.asyncio
async def test_verify_token_username_is_none(mocker, settings, connection):
    mocker.patch("apps.auth.services.jwt.decode", return_value={"type": "bearer"})
    with pytest.raises(HTTPException, match="Could not find token"):
        await verify_token(settings, "extra_secret_jwt_token", "request", connection)


@mark.services
@pytest.mark.asyncio
async def test_verify_token_invalid_token(mocker, settings, connection):
    with pytest.raises(HTTPException, match="Токен доступа не действителен"):
        await verify_token(settings, "extra_secret_jwt_token", "request", connection)


@mark.services
@pytest.mark.asyncio
async def test_verify_token_user_unauthorized(mocker, settings, connection):
    mocker.patch(
        "apps.auth.services.jwt.decode",
        return_value={"sub": "johndoe", "type": "bearer"},
    )
    mocker.patch("apps.auth.services.get_user", return_value=None)
    with pytest.raises(HTTPException, match="Пользователь не авторизован!"):
        await verify_token(settings, "extra_secret_jwt_token", "request", connection)


@mark.services
@pytest.mark.asyncio
async def test_error_middleware_raises():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/middleware-error",
        "headers": [],
    }
    request = Request(scope)

    async def dummy_call_next(req):
        return Response("ok")

    with pytest.raises(HTTPException, match="Токен доступа не действителен"):
        await check_if_user_authorized(request, dummy_call_next)


class AsyncMockResponse:
    def __init__(self, data, status):
        self.data = data
        self.status = status

    async def __aexit__(self, exc_type, exc, tb):
        await asyncio.sleep(0.001)

    async def __aenter__(self):
        await asyncio.sleep(0.001)
        return self

    def json(self):
        return self


@mark.services
@pytest.mark.asyncio
async def test_fetch_external_API_data_success(mocker):
    data = {"message": "ok"}
    response = AsyncMockResponse(data=data, status=200)
    mock = mocker.patch(
        "apps.external_API.services.httpx.AsyncClient.get", return_value=response
    )
    resp = await fetch_data("https://jsonplaceholder.typicode.com/posts")
    assert resp.status == 200
    assert resp.data == {"message": "ok"}
    mock.assert_called_once_with("https://jsonplaceholder.typicode.com/posts")
