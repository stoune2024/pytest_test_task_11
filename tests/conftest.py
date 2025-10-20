from dataclasses import dataclass

import pytest
import pytest_asyncio

from apps.user.services import get_connection, AsyncDatabaseConnection
from apps.user.schemas import UserPublic
from apps.user.routers import middleware_protected_app
from apps.auth.services import verify_token
from apps.auth.schemas import TokenData
from settings.settings import settings as project_settings
from main import app
import asyncio


@pytest_asyncio.fixture
def settings():
    """
    Фикстура, возвращающая настройки пользователя
    :return: экземпляр класса с настройками
    """

    @dataclass
    class Settings:
        DB_HOST = "postgres"
        DB_PORT = 5432
        DB_USER = "postgres"
        DB_PASS = "postgres"
        DB_NAME = "postgres"
        TEST_DB_NAME = "test_postgres"
        SECRET_KEY = "super_secret_key"
        ALGORITHM = "super_secret_algorithm"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        REFRESH_TOKEN_EXPIRE_DAYS = 3

    settings_instance = Settings()
    return settings_instance


@pytest_asyncio.fixture
async def connection():
    """
    Фикстура, возвращающая асинхронное подключение к БД
    :return: Подключение для взаимодействия с тестировочной БД
    """
    async with AsyncDatabaseConnection(project_settings.test_db_url) as connection:
        await asyncio.sleep(0.01)
        yield connection


@pytest_asyncio.fixture
async def protection():
    """
    Фикстура, возвращающая имитацию защищенного подключения
    :return: Защищенное подключение
    """
    await asyncio.sleep(0.001)
    token = TokenData(username="secret_username")
    return token


@pytest.fixture
def user_public():
    """
    Фикстура, возвращающая словарь с данными пользователя, соответствующими UserPublic
    :return: словарь с данными пользователя
    """
    user = UserPublic(
        id=1,
        name="John",
        age=35,
        is_supervisor=True,
        email="johndoe@mail.com",
        phone_number="+8 (800) 555-35-35",
    )
    user_dict = user.model_dump()
    return user_dict


@pytest.fixture
def list_of_user_create():
    """
    Фикстура, возвращающая список со словарями пользователей
    :return: лист со словарями пользователей UserCreate
    """
    return [
        {
            "id": i,
            "name": f"User_{i}",
            "age": (i + 1) * 10,
            "is_supervisor": False,
            "email": f"user_{i}@mail.com",
            "phone_number": f"+8 ({i}00) 555-35-35",
            "username": f"username_{i}",
            "password": f"password_{i}",
        }
        for i in range(5)
    ]


@pytest.fixture(autouse=True)
def override_dependencies(connection, protection):
    """
    Фикстура, автоматически срабатывающая перед каждым тестом и переписывающая зависимости
    :param connection: Зависимость соединения
    :param protection: Зависимость защиты
    """

    def get_connection_override():
        return connection

    def get_protection_override():
        return protection

    app.dependency_overrides[get_connection] = get_connection_override
    app.dependency_overrides[verify_token] = get_protection_override
    middleware_protected_app.dependency_overrides[get_connection] = (
        get_connection_override
    )
    yield
    app.dependency_overrides.clear()
    middleware_protected_app.dependency_overrides.clear()
