import asyncio

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status

from app.schemas import TranscriptResponse, TtsRequest, VoicesResponse
from app.services.edge_tts_service import EdgeTtsError, available_voices, generate_speech
from app.services.groq_stt import GroqSttError, transcribe

router = APIRouter(prefix="/api", tags=["speech"])
ALLOWED_AUDIO_TYPES = {"audio/webm", "audio/ogg", "audio/wav", "audio/mp4", "audio/mpeg"}
MAX_AUDIO_BYTES = 10 * 1024 * 1024


# ==============================================================================
# PHASE 3: THE MOUTH (Voice Catalog Endpoint)
# ==============================================================================
@router.get("/voices", response_model=VoicesResponse)
async def voices() -> VoicesResponse:
    """
    TODO (Phase 3 - Step 8):
    Return available Edge-TTS neural voices.
    """
    # Fill here using the workshop prompt
    pass


# ==============================================================================
# PHASE 3: THE MOUTH (Text-to-Speech Streaming Endpoint)
# ==============================================================================
@router.post("/tts", response_class=Response)
async def tts(request: TtsRequest) -> Response:
    """
    TODO (Phase 3 - Step 8):
    Convert reply text into MP3 audio stream.
    1. Validate request.text is non-blank (raise 422 if blank).
    2. Await generate_speech(text, request.voice_id).
    3. Return Response(content=audio, media_type="audio/mpeg").
    """
    # Fill here using the workshop prompt
    pass


# ==============================================================================
# PHASE 1: THE EARS (Audio Transcription Upload Endpoint)
# ==============================================================================
@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_audio(audio: UploadFile = File(...)) -> TranscriptResponse:
    """
    TODO (Phase 1 - Step 3):
    Accept microphone audio recording and return transcribed text.
    1. Validate audio.content_type is in ALLOWED_AUDIO_TYPES (raise 415 if invalid).
    2. Read payload bytes; validate non-empty (422) and under MAX_AUDIO_BYTES (413).
    3. Call transcribe() via asyncio.to_thread.
    4. Return TranscriptResponse(transcript=transcript).
    """
    # Fill here using the workshop prompt
    pass
