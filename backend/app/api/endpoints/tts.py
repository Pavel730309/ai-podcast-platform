"""
API endpoints for TTS
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import Optional, List
import uuid
from pathlib import Path

from app.schemas import (
    TTSRequest,
    TTSResponse,
    VoiceProfileResponse
)
from app.services.tts import TTSService
from app.config import settings

router = APIRouter(prefix="/tts", tags=["tts"])

# Initialize service
tts_service = TTSService()


@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text
    
    - **text**: Text to synthesize (max 5000 characters)
    - **provider**: TTS provider (openai, elevenlabs, google)
    - **voice_id**: Voice identifier
    - **speed**: Speech speed (0.5 to 2.0)
    """
    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
    
    result = await tts_service.synthesize(
        text=request.text,
        voice_id=request.voice_id,
        provider=request.provider,
        speed=request.speed
    )
    
    if result.error:
        raise HTTPException(status_code=400, detail=result.error)
    
    # Save audio file
    audio_id = str(uuid.uuid4())
    audio_dir = Path(settings.UPLOAD_DIR) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    audio_file = audio_dir / f"{audio_id}.{result.format}"
    with open(audio_file, "wb") as f:
        f.write(result.audio_data)
    
    return TTSResponse(
        audio_url=f"/api/tts/audio/{audio_id}",
        duration_seconds=result.duration_seconds,
        provider=result.provider,
        voice_id=result.voice_id
    )


@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """
    Get synthesized audio file
    
    - **audio_id**: Audio file ID
    """
    audio_dir = Path(settings.UPLOAD_DIR) / "audio"
    
    # Find audio file
    for ext in ["mp3", "wav"]:
        audio_file = audio_dir / f"{audio_id}.{ext}"
        if audio_file.exists():
            media_type = "audio/mpeg" if ext == "mp3" else "audio/wav"
            with open(audio_file, "rb") as f:
                return Response(
                    content=f.read(),
                    media_type=media_type
                )
    
    raise HTTPException(status_code=404, detail="Audio file not found")


@router.get("/voices", response_model=List[VoiceProfileResponse])
async def get_voices(
    provider: Optional[str] = None,
    language: Optional[str] = None
):
    """
    Get available voices
    
    - **provider**: Filter by provider (optional)
    - **language**: Filter by language (optional)
    """
    voices = await tts_service.get_voices(provider, language)
    
    return [
        VoiceProfileResponse(
            id=f"{v.provider}_{v.id}",
            provider=v.provider,
            voice_id=v.id,
            name=v.name,
            gender=v.gender.value,
            language=v.language,
            description=v.description,
            preview_url=v.preview_url
        )
        for v in voices
    ]


@router.get("/providers")
async def get_providers():
    """Get list of available TTS providers"""
    return {
        "providers": tts_service.get_available_providers()
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """Get TTS cache statistics"""
    return {
        "cache_size_bytes": tts_service.get_cache_size(),
        "cache_size_mb": round(tts_service.get_cache_size() / (1024 * 1024), 2)
    }


@router.delete("/cache")
async def clear_cache():
    """Clear TTS cache"""
    tts_service.clear_cache()
    return {"message": "Cache cleared successfully"}
