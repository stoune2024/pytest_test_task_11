import asyncio
from typing import Annotated, Any
from fastapi import Depends
from settings.settings import settings
from apps.user.schemas import User
from apps.user.repository import users_store_instance


class AsyncDatabaseConnection:
    """
    Асинхронный контекстный менеджер, имитирующий подключение к БД
    """

    def __init__(self, db_url):
        self.db_url = db_url

    async def __aenter__(self):
        try:
            await asyncio.sleep(0.05)  # Имитация ожидания подключения к БД
            print(f"Асинхронное подключение к базе данных с URL: {self.db_url}")
            return self
        except Exception as e:
            print(f"Ошибка при подключении к БД: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await asyncio.sleep(0.05)  # Имитация ожидания отключения от БД
            print(f"Отключение от базы данных с URL: {self.db_url}")
            print("Отключение от базы данных")
        except Exception as e:
            print(f"Ошибка при разрыве подключения с БД: {e}")

    async def create_user(self, user: User):
        await asyncio.sleep(0.05)
        user_dict = user.model_dump()
        users_store_instance(user_dict)

    async def read_user_by_id(self, user_id):
        await asyncio.sleep(0.05)
        users_list = users_store_instance.users_store
        for i in users_list:
            if i["id"] == user_id:
                return i

    async def read_user_by_username(self, username):
        await asyncio.sleep(0.05)
        users_list = users_store_instance.users_store
        for i in users_list:
            if i["username"] == username:
                return i

    async def read_users(self, start, end):
        await asyncio.sleep(0.05)
        users_list = users_store_instance.users_store
        if start is None and end is None:
            return users_list
        return users_list[start - 1 : end]

    async def delete_user(self, user_id):
        await asyncio.sleep(0.05)
        users_list = users_store_instance.users_store
        for i in users_list:
            if i["id"] == user_id:
                users_list.remove(i)


async def get_connection():
    async with AsyncDatabaseConnection(settings.db_url) as connection:
        await asyncio.sleep(0.05)
        yield connection


ConnectionDep = Annotated[Any, Depends(get_connection)]
