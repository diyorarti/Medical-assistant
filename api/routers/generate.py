from fastapi import APIRouter, Depends

from api.core.security import verify_api_key
from api.schemas.models import GenerateResponse, GenerateRequest
from api.services.hf_client import hf_client

router = APIRouter(prefix="/v1")

@router.post("/generate", response_model=GenerateResponse, dependencies=[Depends(verify_api_key)])
async def generate(req:GenerateRequest):
    text  = await hf_client.generate(
        prompt=req.prompt,
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
    )

    return GenerateResponse(output_text=text)