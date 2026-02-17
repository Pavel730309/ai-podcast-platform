"""
API endpoints for audio processing
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Optional
import uuid
from pathlib import Path
import io

from app.schemas import (
    TTSResponse,
    FileUploadResponse
)
from app.services.audio import AudioProcessor
from app.services.tts import TTSService

router = APIRouter(prefix="/audio", tags=["audio"])

# Initialize services
audio_processor = AudioProcessor()
tts_service = TTSService()


@router.post("/combine", response_model=FileUploadResponse)
async def combine_audio_segments(
    segments: List[UploadFile] = File(...),
    segment_durations: List[float] = File(...),
    output_format: str = "mp3"
):
    """
    Combine multiple audio segments into one
    
    - **segments**: List of audio files to combine
    - **segment_durations**: List of durations for each segment
    - **output_format**: Output format (mp3, wav, flac)
    """
    if len(segments) != len(segment_durations):
        raise HTTPException(status_code=400, detail="Number of segments must match number of durations")
    
    try:
        # Read audio data
        audio_data_list = []
        for segment in segments:
            content = await segment.read()
            audio_data_list.append(content)
        
        # Combine audio
        combined_audio = await audio_processor.combine_audio_segments(
            audio_data_list,
            segment_durations,
            output_format
        )
        
        # Save to file
        audio_id = str(uuid.uuid4())
        audio_dir = Path("uploads/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        audio_file = audio_dir / f"{audio_id}.{output_format}"
        with open(audio_file, "wb") as f:
            f.write(combined_audio)
        
        return FileUploadResponse(
            file_id=audio_id,
            filename=f"combined.{output_format}",
            file_type=output_format,
            file_size=len(combined_audio)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error combining audio: {str(e)}")


@router.post("/add-music", response_model=FileUploadResponse)
async def add_background_music(
    speech_file: UploadFile = File(...),
    music_file: UploadFile = File(...),
    music_volume_ratio: float = 0.3,
    fade_duration: int = 2000
):
    """
    Add background music to speech audio
    
    - **speech_file**: Speech audio file
    - **music_file**: Background music file
    - **music_volume_ratio**: Volume ratio for music (0.0 to 1.0)
    - **fade_duration**: Fade duration in milliseconds
    """
    try:
        # Read audio data
        speech_data = await speech_file.read()
        music_data = await music_file.read()
        
        # Add music
        processed_audio = await audio_processor.add_background_music(
            speech_data,
            music_data,
            music_volume_ratio,
            fade_duration
        )
        
        # Save to file
        audio_id = str(uuid.uuid4())
        audio_dir = Path("uploads/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        audio_file = audio_dir / f"{audio_id}.mp3"
        with open(audio_file, "wb") as f:
            f.write(processed_audio)
        
        return FileUploadResponse(
            file_id=audio_id,
            filename="processed_audio.mp3",
            file_type="mp3",
            file_size=len(processed_audio)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding background music: {str(e)}")


@router.post("/normalize", response_model=FileUploadResponse)
async def normalize_audio(
    audio_file: UploadFile = File(...),
    target_db: float = -20.0
):
    """
    Normalize audio to target dB level
    
    - **audio_file**: Audio file to normalize
    - **target_db**: Target dB level
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Normalize audio
        normalized_audio = await audio_processor.normalize_audio(
            audio_data,
            target_db
        )
        
        # Save to file
        audio_id = str(uuid.uuid4())
        audio_dir = Path("uploads/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        audio_file = audio_dir / f"{audio_id}.mp3"
        with open(audio_file, "wb") as f:
            f.write(normalized_audio)
        
        return FileUploadResponse(
            file_id=audio_id,
            filename="normalized_audio.mp3",
            file_type="mp3",
            file_size=len(normalized_audio)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error normalizing audio: {str(e)}")


@router.get("/info/{audio_id}")
async def get_audio_info(audio_id: str):
    """
    Get information about an audio file
    
    - **audio_id**: Audio file ID
    """
    try:
        # In a real implementation, this would read from storage
        # For now, returning dummy data
        return {
            "audio_id": audio_id,
            "duration_ms": 180000,  # 3 minutes
            "channels": 2,
            "sample_rate": 22050,
            "bit_depth": 16,
            "size_bytes": 45000000
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting audio info: {str(e)}")
