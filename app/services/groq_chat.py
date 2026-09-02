import requests

from app.settings import settings

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM_PROMPT = (
    "You are Jarvis, an advanced and concise desktop voice assistant for Windows. "
    "Answer directly in plain text, normally within two to three short sentences. "
    "You can open allowlisted Windows desktop applications directly on command: Calculator, Notepad, File Explorer, and Visual Studio Code. "
    "You can also open any website or URL, perform Google web searches, search videos on YouTube, and find music on Spotify."
)


class GroqChatError(RuntimeError):
    def __init__(self, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.status_code = status_code


# ==============================================================================
# PHASE 2: THE BRAIN (Groq Chat Completion Generator)
# ==============================================================================
def generate_reply(history: list[dict[str, str]], user_text: str) -> str:
    """
    TODO (Phase 2 - Step 5):
    Send system prompt + conversation history + user text to Groq LLM completions.
    1. Verify settings.groq_api_key is set (raise GroqChatError if not).
    2. Build messages payload with SYSTEM_PROMPT, history, and new user_text.
    3. Send POST request to GROQ_CHAT_URL with temperature 0.4 and max_tokens 220.
    4. Return the trimmed assistant reply text.
    """
    if not settings.groq_api_key:
        raise GroqChatError("Groq is not configured.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": user_text}]
    try:
        response = requests.post(
            GROQ_CHAT_URL,
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json={"model": settings.groq_chat_model, "messages": messages, "temperature": 0.4, "max_tokens": 220},
            timeout=30,
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        raise GroqChatError("Groq could not generate a reply.") from error
    if not reply:
        raise GroqChatError("Groq returned an empty reply.")
    return reply
