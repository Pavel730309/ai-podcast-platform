"""
TTS synthesis tasks for Celery
"""

import asyncio
from typing import List, Dict
from celery import shared_task
from app.services.tts.tts_service import TTSService
from app.services.audio.audio_processor import AudioProcessor


@shared_task(bind=True, max_retries=3)
def synthesize_speech(self, text: str, voice_id: str, provider: str = "openai") -> Dict:
    """
    Synthesize speech from text

    Args:
        text: Text to synthesize
        voice_id: Voice identifier
        provider: TTS provider to use

    Returns:
        Dict with audio data and metadata
    """
    return asyncio.run(_synthesize_speech_async(self, text, voice_id, provider))


async def _synthesize_speech_async(task, text: str, voice_id: str, provider: str):
    """Async implementation of TTS synthesis"""
    try:
        tts_service = TTSService()

        result = await tts_service.synthesize(
            text=text, voice_id=voice_id, provider=provider, use_cache=True
        )

        if result.error:
            raise Exception(result.error)

        return {
            "status": "success",
            "audio_data": result.audio_data.hex(),  # Convert to hex for JSON serialization
            "duration_seconds": result.duration_seconds,
            "provider": result.provider,
            "voice_id": result.voice_id,
        }

    except Exception as exc:
        # Retry with exponential backoff
        countdown = 60 * (2**self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True, max_retries=3)
def synthesize_dialogue(
    self, dialogue: List[Dict], voice_assignments: Dict[str, str]
) -> Dict:
    """
    Synthesize entire dialogue with multiple voices

    Args:
        dialogue: List of dialogue lines with participant and text
        voice_assignments: Mapping of participant names to voice IDs

    Returns:
        Dict with combined audio data
    """
    return asyncio.run(_synthesize_dialogue_async(self, dialogue, voice_assignments))


async def _synthesize_dialogue_async(
    task, dialogue: List[Dict], voice_assignments: Dict[str, str]
):
    """Async implementation of dialogue synthesis"""
    try:
        tts_service = TTSService()
        audio_processor = AudioProcessor()

        audio_segments = []
        segment_durations = []

        # Synthesize each line
        for i, line in enumerate(dialogue):
            participant = line.get("participant", "")
            text = line.get("text", "")

            voice_id = voice_assignments.get(participant, "alloy")

            result = await tts_service.synthesize(
                text=text, voice_id=voice_id, provider="openai", use_cache=True
            )

            if result.error:
                raise Exception(f"TTS failed for line {i}: {result.error}")

            audio_segments.append(result.audio_data)
            segment_durations.append(result.duration_seconds)

            # Update task progress
            progress = (i + 1) / len(dialogue) * 100
            task.update_state(
                state="PROGRESS",
                meta={
                    "progress": progress,
                    "current_line": i + 1,
                    "total_lines": len(dialogue),
                },
            )

        # Combine all segments
        combined_audio = await audio_processor.combine_audio_segments(
            segments=audio_segments,
            segment_durations=segment_durations,
            output_format="mp3",
        )

        return {
            "status": "success",
            "audio_data": combined_audio.hex(),
            "duration_seconds": sum(segment_durations),
            "num_segments": len(dialogue),
        }

    except Exception as exc:
        countdown = 60 * (2**task.request.retries)
        raise task.retry(exc=exc, countdown=countdown)


@shared_task
def clear_tts_cache():
    """Clear TTS cache to free up space"""
    tts_service = TTSService()
    cache_size_before = tts_service.get_cache_size()

    # Clear cache files older than 7 days
    import os
    import time
    from pathlib import Path

    cache_dir = Path("cache/tts")
    if cache_dir.exists():
        current_time = time.time()
        for file in cache_dir.glob("*"):
            if file.is_file():
                # Check if file is older than 7 days
                if current_time - file.stat().st_mtime > 7 * 24 * 3600:
                    try:
                        file.unlink()
                    except:
                        pass

    cache_size_after = tts_service.get_cache_size()

    return {
        "status": "success",
        "cleared_bytes": cache_size_before - cache_size_after,
        "cache_size_before": cache_size_before,
        "cache_size_after": cache_size_after,
    }
