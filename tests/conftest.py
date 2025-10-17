from dataclasses import dataclass

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from apps.user.services import get_connection, AsyncDatabaseConnection
from apps.user.schemas import UserPublic
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


@pytest.fixture
def client(connection):
    """
    Фикстура, возврвщающая клиента
    :param connection: Фикстура, возвращающая подключение
    :return: Тестовый клиент, имитирующий REST API
    """

    def get_session_override():
        return connection

    app.dependency_overrides[get_connection] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


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
