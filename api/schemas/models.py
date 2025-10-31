from pydantic import BaseModel
from typing import List, Optional

# /v1/generate
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.9

class GenerateResponse(BaseModel):
    output_text: str

# OpenAI-style chat
class ChatMessage(BaseModel):
    role: str   # "system" | "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    model: str = "your-model"
    messages: List[ChatMessage]
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9

class ChatChoiceMessage(BaseModel):
    role: str
    content: str

class ChatChoice(BaseModel):
    index: int
    finish_reason: str
    message: ChatChoiceMessage

class ChatUsage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    model: str
    choices: list[ChatChoice]
    usage: ChatUsage = ChatUsage()
