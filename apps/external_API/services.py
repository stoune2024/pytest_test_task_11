from typing import Any

import httpx


async def fetch_data() -> list[dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://jsonplaceholder.typicode.com/posts")
    return response.json()
