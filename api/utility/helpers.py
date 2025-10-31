from api.schemas.models import ChatRequest

def hf_prompt(req: ChatRequest) -> str:
    parts: list[str] = []
    for m in req.messages:
        role = m.role.lower()
        if role == "system":
            parts.append(f"<system>{m.content}</system>")
        elif role == "user":
            parts.append(f"<user>{m.content}</user>")
        else:
            parts.append(f"<assistant>{m.content}</assistant>")
    parts.append("<assistant>")
    return "\n".join(parts)