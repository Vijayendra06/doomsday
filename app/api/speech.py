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
    return VoicesResponse(voices=available_voices())


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
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Speech text cannot be blank.")
    try:
        audio = await generate_speech(request.text.strip(), request.voice_id)
    except EdgeTtsError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return Response(content=audio, media_type="audio/mpeg")


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
    if audio.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported audio type.")
    payload = await audio.read()
    if not payload:
        raise HTTPException(status_code=422, detail="Audio payload cannot be empty.")
    if len(payload) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Audio payload is too large.")
    try:
        transcript = await asyncio.to_thread(transcribe, payload, audio.filename or "recording", audio.content_type)
    except GroqSttError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return TranscriptResponse(transcript=transcript)
