import httpx
import asyncio
from app.core.config import settings


class AIClient:

    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.base_url = settings.AI_API_URL

    async def generate(self, prompt: str, expect_json: bool = False):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }

        if expect_json:
            payload["response_format"] = {"type": "json_object"}

        timeout = httpx.Timeout(30.0, connect=10.0)

        limits = httpx.Limits(max_connections=10, max_keepalive_connections=5) 

        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            for attempt in range(3):
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )

                    data = response.json()

                    if response.status_code != 200:
                        raise Exception(f"AI API error {response.status_code}: {data}")

                    return data["choices"][0]["message"]["content"]

                except httpx.ConnectTimeout:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2)