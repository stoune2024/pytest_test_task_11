from datetime import timedelta
from apps.auth.services import (
    get_user,
    authenticate_user,
    create_access_token,
    verify_token,
)
from fastapi import HTTPException
import pytest


@pytest.mark.asyncio
async def test_get_user_success(mocker, connection):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe"},
    )
    result = await get_user("johndoe", connection)
    assert result == {"id": 1, "username": "johndoe"}


@pytest.mark.asyncio
async def test_get_user_not_found(mocker):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe"},
    )
    with pytest.raises(HTTPException, match="Пользователь не найден"):
        await get_user("johndoe", "connection")


@pytest.mark.asyncio
async def test_authenticate_user_success(mocker, connection):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe", "hashed_password": "johncoffee"},
    )
    mocker.patch("apps.auth.services.CryptContext.verify", return_value=True)
    result = await authenticate_user("username", "johncoffee", connection)
    assert result == {"id": 1, "username": "johndoe", "hashed_password": "johncoffee"}


@pytest.mark.asyncio
async def test_authenticate_user_not_found(mocker):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe", "hashed_password": "johncoffee"},
    )
    with pytest.raises(HTTPException, match="Пользователь не найден"):
        await authenticate_user("username", "johncoffee", "connection")


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(mocker, connection):
    mocker.patch(
        "apps.user.services.AsyncDatabaseConnection.read_user_by_username",
        return_value={"id": 1, "username": "johndoe", "hashed_password": "johncoffee"},
    )
    mocker.patch("apps.auth.services.CryptContext.verify", return_value=False)
    with pytest.raises(HTTPException, match="Введен неверный пароль"):
        await authenticate_user("username", "johncoffee", connection)


@pytest.mark.asyncio
async def test_create_access_token(mocker, settings):
    mocker.patch("apps.auth.services.jwt.encode", return_value="encoded_jwt_token")
    result = await create_access_token(
        settings,
        {"sub": "johndoe"},
        timedelta(days=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    assert result == "encoded_jwt_token"


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


@pytest.mark.asyncio
async def test_verify_token_username_is_none(mocker, settings, connection):
    mocker.patch("apps.auth.services.jwt.decode", return_value={"type": "bearer"})
    with pytest.raises(HTTPException, match="Could not find token"):
        await verify_token(settings, "extra_secret_jwt_token", "request", connection)


@pytest.mark.asyncio
async def test_verify_token_invalid_token(mocker, settings, connection):
    with pytest.raises(HTTPException, match="Токен доступа не действителен"):
        await verify_token(settings, "extra_secret_jwt_token", "request", connection)


@pytest.mark.asyncio
async def test_verify_token_user_unauthorized(mocker, settings, connection):
    mocker.patch(
        "apps.auth.services.jwt.decode",
        return_value={"sub": "johndoe", "type": "bearer"},
    )
    with pytest.raises(HTTPException, match="Пользователь не авторизован!"):
        await verify_token(settings, "extra_secret_jwt_token", "request", connection)
