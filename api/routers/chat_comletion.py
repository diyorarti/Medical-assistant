from fastapi import APIRouter, Depends
from api.core.config import settings
from api.schemas.models import ChatRequest, ChatCompletionResponse, ChatChoice, ChatChoiceMessage
from api.services.hf_client import hf_client
from api.core.security import verify_api_key
from api.utility.helpers import hf_prompt


router = APIRouter(prefix="/v1")

@router.post("/chat/completions", response_model=ChatCompletionResponse, dependencies=[Depends(verify_api_key)])
async def chat_completions(req:ChatRequest):
    prompt = hf_prompt(req)
    text = await hf_client.chat_completion(
        formatted_prompt=prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p
    )
    return ChatCompletionResponse(
        id="chatcmpl-1",
        model=req.model,
        choices=[
            ChatChoice(
                index=0,
                finish_reason="stop",
                message=ChatChoiceMessage(role="assistant", content=text),
            )
        ],
    )