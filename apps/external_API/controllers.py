from typing import Annotated, Union

from fastapi import Query

from apps.external_API.routers import external_API_router
from apps.external_API.services import fetch_data


@external_API_router.get("/json", response_model=Union[list[dict], dict])
async def fetch_external_API_data(
    offset: Annotated[
        int,
        Query(
            title="Отступ от начала списка",
            description="ID сущности, с которой начать поиск",
            ge=1,
            le=99,
        ),
    ] = 1,
    limit: Annotated[
        int,
        Query(
            title="Ограничитель списка",
            description="ID сущности, которой закончить поиск",
            ge=1,
            le=101,
        ),
    ] = 101,
):
    """
    Эндпоинт поиска диапазона сущностей.
    :param offset: Отступ. Рекомендуется использовать 1 по умолчанию
    :param limit: Ограничитель.
    :return: Список сущностей или ошибка.
    """
    try:
        result = await fetch_data("https://jsonplaceholder.typicode.com/posts")
        return result[offset - 1 : offset - 2 + limit]
    except Exception as e:
        return {"message": e}
