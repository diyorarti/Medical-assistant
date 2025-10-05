import os
import asyncio
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

import time
from fastapi import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from typing import Optional

from fastapi.middleware.cors import CORSMiddleware


REQUEST_COUNT = Counter(
    "api_requests_total", "Total API requests", ["path", "method"]
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Request latency in seconds", ["path", "method"]
)
RESPONSE_STATUS = Counter(
    "api_response_status_total", "Responses by HTTP status", ["path", "method", "status"]
)


load_dotenv()  

HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")
HF_API_TOKEN    = os.getenv("HF_API_TOKEN")
API_KEYS        = set((os.getenv("API_KEYS") or "").split(","))  

if not HF_ENDPOINT_URL or not HF_API_TOKEN:
    raise RuntimeError("HF_ENDPOINT_URL or HF_API_TOKEN missing. Check your .env")

def _pick_api_key(x_api_key: Optional[str] = Header(None),
                  authorization: Optional[str] = Header(None)) -> str:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    raise HTTPException(status_code=401, detail="Missing API key")

def key_by_api_key(request: Request) -> str:
    # Prefer Authorization: Bearer <key> if present
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    # Fallback to X-API-Key header, then IP
    return request.headers.get("x-api-key") or request.client.host


limiter = Limiter(key_func=key_by_api_key)
app = FastAPI(title="Medical Assistant API", version="1.0.0")
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "X-API-Key", "Content-Type"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    REQUEST_COUNT.labels(path, method).inc()
    start = time.perf_counter()
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        elapsed = time.perf_counter() - start
        REQUEST_LATENCY.labels(path, method).observe(elapsed)
        
        try:
            RESPONSE_STATUS.labels(path, method, str(status)).inc()
        except Exception:
            pass
        
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please try again later."})

def _require_api_key(key: str):
    if key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

# --- models ---
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.9

# --- routes ---
@app.get("/")
def home():
    return {"message": "Model API is running successfully 🚀"}

@app.post("/v1/generate")
@limiter.limit("20/minute")
async def generate(request: Request,
                   req: GenerateRequest,
                   x_api_key: Optional[str] = Header(None),
                   authorization: Optional[str] = Header(None)):
    key = _pick_api_key(x_api_key, authorization)
    _require_api_key(key)

    payload = {
        "inputs": req.prompt,
        "parameters": {
            "max_new_tokens": req.max_new_tokens,
            "temperature": req.temperature,
            "top_p": req.top_p,
            "return_full_text": False,
        }
    }
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                r = await client.post(HF_ENDPOINT_URL, headers=headers, json=payload)
                if r.status_code >= 500:
                    if attempt < 2:
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    raise HTTPException(status_code=502, detail=f"HuggingFace error {r.status_code}: {r.text}")
                if r.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"HuggingFace error {r.status_code}: {r.text}")

                data = r.json()
                if isinstance(data, list):
                    data = data[0]
                text = data.get("generated_text") or data.get("output_text") or ""
                return {"output_text": text}
        except httpx.ReadTimeout:
            if attempt < 2:
                await asyncio.sleep(2 * (attempt + 1))
                continue
            raise HTTPException(status_code=504, detail="Upstream timeout")
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(2 * (attempt + 1))
                continue
            raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


# ---- OpenAI-style chat schemas ----
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "your-model"   # for clients; not used by HF
    messages: list[ChatMessage]
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9

@app.post("/v1/chat/completions")
@limiter.limit("20/minute")
async def chat_completions(
    request: Request,
    req: ChatRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    key = _pick_api_key(x_api_key, authorization)
    _require_api_key(key)

    # simple prompt formatting; adapt to your finetune if needed
    prompt = ""
    for m in req.messages:
        role = m.role.lower()
        if role == "system":
            prompt += f"<system>{m.content}</system>\n"
        elif role == "user":
            prompt += f"<user>{m.content}</user>\n"
        else:
            prompt += f"<assistant>{m.content}</assistant>\n"
    prompt += "<assistant>"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": req.max_tokens,
            "temperature": req.temperature,
            "top_p": req.top_p,
            "return_full_text": False,
        },
    }
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # reuse the same retry strategy as generate()
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                r = await client.post(HF_ENDPOINT_URL, headers=headers, json=payload)
                if r.status_code >= 500:
                    if attempt < 2:
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    raise HTTPException(status_code=502, detail=f"HuggingFace error {r.status_code}: {r.text}")
                if r.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"HuggingFace error {r.status_code}: {r.text}")

                data = r.json()
                if isinstance(data, list):
                    data = data[0]
                text = data.get("generated_text") or data.get("output_text") or ""

                return {
                    "id": "chatcmpl-1",
                    "object": "chat.completion",
                    "model": req.model,
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {"role": "assistant", "content": text},
                        }
                    ],
                    "usage": {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None},
                }
        except httpx.ReadTimeout:
            if attempt < 2:
                await asyncio.sleep(2 * (attempt + 1))
                continue
            raise HTTPException(status_code=504, detail="Upstream timeout")
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(2 * (attempt + 1))
                continue
            raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "version": "1.0.0"}
