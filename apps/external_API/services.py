from typing import Any

import httpx


async def fetch_data(url: str) -> list[dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.json()
