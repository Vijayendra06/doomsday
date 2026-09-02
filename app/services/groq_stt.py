import io
import requests

from app.settings import settings

GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class GroqSttError(RuntimeError):
    pass


# ==============================================================================
# PHASE 1: THE EARS (Speech-to-Text with Groq Whisper)
# ==============================================================================
def transcribe(audio: bytes, filename: str, content_type: str) -> str:
    """
    TODO (Phase 1 - Step 2):
    Send user audio recording bytes to Groq Whisper and return transcribed text.
    
    Instructions to fill:
    1. Check if settings.groq_api_key is set. If not, raise GroqSttError("Groq is not configured.")
    2. Set Authorization header with Bearer token.
    3. Build multipart payload with (filename, io.BytesIO(audio), content_type) and model 'whisper-large-v3-turbo'.
    4. Send POST to GROQ_TRANSCRIBE_URL and return the trimmed transcript string.
    """
    if not settings.groq_api_key:
        raise GroqSttError("Groq is not configured.")

    try:
        response = requests.post(
            GROQ_TRANSCRIBE_URL,
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            files={"file": (filename, io.BytesIO(audio), content_type)},
            data={"model": "whisper-large-v3-turbo"},
            timeout=30,
        )
        response.raise_for_status()
        transcript = response.json()["text"].strip()
    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        raise GroqSttError("Groq could not transcribe the audio.") from error
    if not transcript:
        raise GroqSttError("Groq returned an empty transcript.")
    return transcript
