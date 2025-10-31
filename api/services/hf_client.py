import asyncio
import httpx
from fastapi import HTTPException
from api.core.config import settings

class HFClient:
    def __init__(self) -> None:
        self._url = settings.HF_ENDPOINT
        self._headers = {
            "Authorization": f"Bearer {settings.HF_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._timeout = settings.httpx_timeout_seconds
        self._retries = settings.retry_attempts

    async def _post(self, payload: dict) -> dict:
        for attempt in range(self._retries):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    r = await client.post(self._url, headers=self._headers, json=payload)

                if r.status_code >= 500:
                    if attempt < self._retries - 1:
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    raise HTTPException(status_code=502, detail=f"HF error {r.status_code}: {r.text}")
                if r.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"HF error {r.status_code}: {r.text}")

                data = r.json()
                if isinstance(data, list): 
                    data = data[0]
                return data

            except httpx.ReadTimeout:
                if attempt < self._retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                raise HTTPException(status_code=504, detail="Upstream timeout")
            except Exception as e:
                if attempt < self._retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    async def generate(self, prompt: str, max_new_tokens: int, temperature: float, top_p: float) -> str:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "return_full_text": False,
            },
        }
        data = await self._post(payload)
        return data.get("generated_text") or data.get("output_text") or ""

    async def chat_completion(self, formatted_prompt: str, max_tokens: int, temperature: float, top_p: float) -> str:
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "return_full_text": False,
            },
        }
        data = await self._post(payload)
        return data.get("generated_text") or data.get("output_text") or ""

hf_client = HFClient()
