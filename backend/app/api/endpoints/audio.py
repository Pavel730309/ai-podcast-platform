"""
API endpoints for audio processing
"""
import logging
from pathlib import Path
from typing import List
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from app.schemas import FileUploadResponse
from app.services.audio import AudioProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audio", tags=["audio"])

audio_processor = AudioProcessor()

AUDIO_DIR = Path("uploads/audio")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_bytes(data: bytes, suffix: str = ".mp3") -> Path:
    """Save bytes to a unique file in the audio upload directory."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    file_path = AUDIO_DIR / f"{uuid.uuid4()}{suffix}"
    file_path.write_bytes(data)
    return file_path


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/combine", response_model=FileUploadResponse)
async def combine_audio_segments(
    segments: List[UploadFile] = File(...),
    output_format: str = "mp3",
):
    """
    Combine multiple audio segments into one file.

    - **segments**: List of audio files to combine
    - **output_format**: Output format (mp3, wav, flac)
    """
    if not segments:
        raise HTTPException(status_code=400, detail="No audio segments provided")

    try:
        audio_data_list: List[bytes] = []
        durations: List[float] = []

        for seg in segments:
            content = await seg.read()
            audio_data_list.append(content)
            durations.append(0.0)  # duration is computed internally by pydub

        combined = await audio_processor.combine_audio_segments(
            audio_data_list, durations, output_format
        )

        file_path = _save_bytes(combined, suffix=f".{output_format}")

        return FileUploadResponse(
            file_id=file_path.stem,
            filename=f"combined.{output_format}",
            file_type=output_format,
            file_size=len(combined),
        )

    except Exception as e:
        logger.error(f"Error combining audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error combining audio: {str(e)}")


@router.post("/add-music", response_model=FileUploadResponse)
async def add_background_music(
    speech_file: UploadFile = File(...),
    music_file: UploadFile = File(...),
    music_volume_ratio: float = 0.3,
    fade_duration: int = 2000,
):
    """
    Add background music to a speech audio file.

    - **speech_file**: Speech audio file
    - **music_file**: Background music file
    - **music_volume_ratio**: Volume ratio for music (0.0 – 1.0)
    - **fade_duration**: Fade duration in milliseconds
    """
    try:
        speech_data = await speech_file.read()
        music_data = await music_file.read()

        processed = await audio_processor.add_background_music(
            speech_data, music_data, music_volume_ratio, fade_duration
        )

        file_path = _save_bytes(processed)

        return FileUploadResponse(
            file_id=file_path.stem,
            filename="processed_audio.mp3",
            file_type="mp3",
            file_size=len(processed),
        )

    except Exception as e:
        logger.error(f"Error adding background music: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error adding background music: {str(e)}")


@router.post("/normalize", response_model=FileUploadResponse)
async def normalize_audio(
    audio_file: UploadFile = File(...),
    target_db: float = -16.0,
):
    """
    Normalize audio to a target dB level.

    - **audio_file**: Audio file to normalize
    - **target_db**: Target dB level (default: -16.0)
    """
    try:
        audio_data = await audio_file.read()

        normalized = await audio_processor.normalize_audio(audio_data, target_db)

        file_path = _save_bytes(normalized)

        return FileUploadResponse(
            file_id=file_path.stem,
            filename="normalized_audio.mp3",
            file_type="mp3",
            file_size=len(normalized),
        )

    except Exception as e:
        logger.error(f"Error normalizing audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error normalizing audio: {str(e)}")


@router.get("/info/{audio_id}")
async def get_audio_info(audio_id: str):
    """
    Get technical information about a processed audio file.

    - **audio_id**: Audio file ID (UUID stem, without extension)
    """
    # Search for the file in the upload directory
    audio_path: Path | None = None
    for ext in (".mp3", ".wav", ".flac", ".ogg"):
        candidate = AUDIO_DIR / f"{audio_id}{ext}"
        if candidate.exists():
            audio_path = candidate
            break

    if audio_path is None:
        raise HTTPException(status_code=404, detail="Audio file not found")

    try:
        info = await audio_processor.get_audio_info_from_file(str(audio_path))
        info["audio_id"] = audio_id
        info["filename"] = audio_path.name
        return info

    except Exception as e:
        logger.error(f"Error getting audio info for {audio_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting audio info: {str(e)}")


@router.get("/download/{audio_id}")
async def download_audio(audio_id: str):
    """
    Download a processed audio file by its ID.

    - **audio_id**: Audio file ID (UUID stem, without extension)
    """
    audio_path: Path | None = None
    for ext in (".mp3", ".wav", ".flac", ".ogg"):
        candidate = AUDIO_DIR / f"{audio_id}{ext}"
        if candidate.exists():
            audio_path = candidate
            break

    if audio_path is None:
        raise HTTPException(status_code=404, detail="Audio file not found")

    media_type_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".flac": "audio/flac",
        ".ogg": "audio/ogg",
    }
    media_type = media_type_map.get(audio_path.suffix, "application/octet-stream")

    return FileResponse(
        path=str(audio_path),
        media_type=media_type,
        filename=audio_path.name,
    )
