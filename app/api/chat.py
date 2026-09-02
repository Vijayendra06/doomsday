import asyncio

from fastapi import APIRouter, HTTPException, status

from app.schemas import ChatRequest, ChatResponse
from app.services.conversation import ConversationStore
from app.services.groq_chat import GroqChatError, generate_reply

router = APIRouter(prefix="/api", tags=["chat"])
conversation_store = ConversationStore()


# ==============================================================================
# PHASE 2: THE BRAIN (Main Chat Completion API Route)
# ==============================================================================
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    TODO (Phase 2 - Step 6):
    1. Validate request.text is non-blank (raise 422 HTTP error if empty).
    2. Retrieve conversation history from conversation_store.history(session_id).
    3. Call generate_reply() via asyncio.to_thread.
    4. Save the turn using conversation_store.append_turn().
    5. Return ChatResponse(sessionId, reply, turnsRetained).
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Message text cannot be blank.")
    history = conversation_store.history(request.session_id)
    try:
        reply = await asyncio.to_thread(generate_reply, history, text)
    except GroqChatError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
    turns_retained = conversation_store.append_turn(request.session_id, text, reply)
    return ChatResponse(sessionId=request.session_id, reply=reply, turnsRetained=turns_retained)
