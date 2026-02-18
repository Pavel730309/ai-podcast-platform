"""
Podcast processing tasks for Celery
"""

import asyncio
import logging
import uuid
import json
import os
from pathlib import Path
from typing import Optional
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import async_session
from app.models import Podcast, PodcastParticipant, PodcastStatus
from app.services.text_extraction.extraction_service import TextExtractionService
from app.services.scenario.scenario_service import ScenarioService
from app.services.tts.tts_service import TTSService
from app.services.audio.audio_processor import AudioProcessor

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_podcast(self, podcast_id: str):
    """
    Main task for processing a podcast through all stages

    Stages:
    1. Extract text from source
    2. Generate scenario
    3. Synthesize speech
    4. Process and mix audio
    5. Generate cover image
    """
    logger.info(f"Starting podcast processing: {podcast_id}")
    return asyncio.run(_process_podcast_async(self, podcast_id))


async def _process_podcast_async(celery_task, podcast_id: str):
    """Async implementation of podcast processing"""
    async with async_session() as session:
        podcast: Optional[Podcast] = None
        try:
            # Get podcast
            result = await session.execute(
                select(Podcast).where(Podcast.id == podcast_id)
            )
            podcast = result.scalar_one_or_none()

            if not podcast:
                raise ValueError(f"Podcast {podcast_id} not found")

            # ─── Stage 1: Extract text ───────────────────────────────────────
            current_status = podcast.status
            if current_status == PodcastStatus.PENDING:
                await _update_status(session, podcast, PodcastStatus.EXTRACTING_TEXT)
                await session.refresh(podcast)

                source_url = str(podcast.source_url) if podcast.source_url else None
                source_type = str(podcast.source_type) if podcast.source_type else "text"

                if source_url and source_type == "url":
                    logger.info(f"Extracting text from URL: {source_url}")
                    extraction_service = TextExtractionService()
                    extraction_result = await extraction_service.extract_from_url(source_url)
                    if extraction_result.text:
                        podcast.extracted_text = extraction_result.text
                        await session.commit()
                        logger.info(f"Extracted {len(extraction_result.text)} chars from URL")
                    elif extraction_result.error:
                        raise Exception(f"Text extraction failed: {extraction_result.error}")

                # If text already set (from source_text), just move on
                if not podcast.extracted_text:
                    raise Exception("No text available for podcast generation")

            # ─── Stage 2: Generate scenario ──────────────────────────────────
            await session.refresh(podcast)
            if podcast.status == PodcastStatus.EXTRACTING_TEXT:
                await _update_status(session, podcast, PodcastStatus.GENERATING_SCENARIO)
                await session.refresh(podcast)

                extracted_text = str(podcast.extracted_text) if podcast.extracted_text else None
                if not extracted_text:
                    raise Exception("No extracted text for scenario generation")

                logger.info(f"Generating scenario for podcast {podcast_id}")
                scenario_service = ScenarioService()
                style_value = str(podcast.style.value) if podcast.style else "entertainment"
                num_participants = int(podcast.num_participants) if podcast.num_participants else 2

                # Get participant names from DB
                participants_result = await session.execute(
                    select(PodcastParticipant).where(
                        PodcastParticipant.podcast_id == podcast_id
                    )
                )
                participants = participants_result.scalars().all()
                participant_roles = [p.role for p in participants] if participants else None

                scenario_result = await scenario_service.generate_scenario(
                    text=extracted_text,
                    style=style_value,
                    num_participants=num_participants,
                    participant_roles=participant_roles,
                )

                if scenario_result.error:
                    raise Exception(f"Scenario generation failed: {scenario_result.error}")

                podcast.scenario = scenario_service.scenario_to_json(scenario_result)
                await session.commit()
                logger.info(f"Generated scenario with {len(scenario_result.dialogue)} lines")

            # ─── Stage 3: Synthesize speech ──────────────────────────────────
            await session.refresh(podcast)
            if podcast.status == PodcastStatus.GENERATING_SCENARIO:
                await _update_status(session, podcast, PodcastStatus.SYNTHESIZING_SPEECH)
                await session.refresh(podcast)

                scenario_text = str(podcast.scenario) if podcast.scenario else None
                if not scenario_text:
                    raise Exception("No scenario for speech synthesis")

                logger.info(f"Synthesizing speech for podcast {podcast_id}")
                scenario_service = ScenarioService()
                scenario_result = scenario_service.json_to_scenario(podcast.scenario)

                if not scenario_result or not scenario_result.dialogue:
                    raise Exception("Invalid scenario format")

                # Get participant voice settings
                participants_result = await session.execute(
                    select(PodcastParticipant).where(
                        PodcastParticipant.podcast_id == podcast_id
                    )
                )
                participants = participants_result.scalars().all()

                # Build voice map: participant name -> voice_id
                voice_map = {}
                for p in participants:
                    voice_map[p.name] = {
                        "voice_id": p.voice_id,
                        "provider": p.voice_provider,
                    }

                tts_service = TTSService()
                audio_result = await tts_service.synthesize_dialogue(
                    scenario_result.dialogue,
                    voice_map=voice_map,
                )

                if not audio_result or not audio_result.file_path:
                    raise Exception("TTS synthesis failed - no audio file produced")

                podcast.audio_file = audio_result.file_path
                await session.commit()
                logger.info(f"Speech synthesized: {audio_result.file_path}")

            # ─── Stage 4: Process audio ──────────────────────────────────────
            await session.refresh(podcast)
            if podcast.status == PodcastStatus.SYNTHESIZING_SPEECH:
                await _update_status(session, podcast, PodcastStatus.PROCESSING_AUDIO)
                await session.refresh(podcast)

                audio_file = str(podcast.audio_file) if podcast.audio_file else None
                if not audio_file:
                    raise Exception("No audio file for processing")

                logger.info(f"Processing audio for podcast {podcast_id}")
                audio_processor = AudioProcessor()

                # Mix with background music
                try:
                    style_value = str(podcast.style.value) if podcast.style else "entertainment"
                    music_category = {
                        "academic": "ambient",
                        "entertainment": "corporate",
                        "business": "corporate",
                    }.get(style_value, "corporate")

                    mixed_result = await audio_processor.mix_audio_with_music(
                        audio_file,
                        music_category=music_category,
                    )
                    if mixed_result and mixed_result.file_path:
                        podcast.audio_file = mixed_result.file_path
                        if hasattr(mixed_result, "duration_seconds") and mixed_result.duration_seconds:
                            podcast.duration_seconds = int(mixed_result.duration_seconds)
                except Exception as mix_err:
                    logger.warning(f"Audio mixing failed (using raw audio): {mix_err}")
                    # Continue with raw audio if mixing fails

                await session.commit()
                logger.info(f"Audio processed: {podcast.audio_file}")

            # ─── Stage 5: Generate cover ─────────────────────────────────────
            await session.refresh(podcast)
            if podcast.status == PodcastStatus.PROCESSING_AUDIO:
                await _update_status(session, podcast, PodcastStatus.GENERATING_COVER)
                await session.refresh(podcast)

                logger.info(f"Generating cover for podcast {podcast_id}")
                title = str(podcast.title) if podcast.title else "Podcast"
                description = str(podcast.description) if podcast.description else ""

                try:
                    from app.services.image_generation.image_generator import ImageGenerator
                    image_generator = ImageGenerator()

                    # generate_cover() returns bytes (PNG image data)
                    cover_bytes = await image_generator.generate_cover(
                        title=title,
                        description=description,
                        style="modern",
                    )

                    if cover_bytes:
                        # Save bytes to file
                        cover_dir = Path("uploads/covers")
                        cover_dir.mkdir(parents=True, exist_ok=True)
                        cover_path = str(cover_dir / f"{uuid.uuid4()}.png")
                        with open(cover_path, "wb") as f:
                            f.write(cover_bytes)
                        podcast.cover_image = cover_path
                        logger.info(f"Cover saved: {cover_path}")
                    else:
                        raise ValueError("Empty cover image returned")

                except Exception as cover_err:
                    logger.warning(f"Cover generation failed, using placeholder: {cover_err}")
                    try:
                        cover_path = await _generate_placeholder_cover(title)
                        if cover_path:
                            podcast.cover_image = cover_path
                    except Exception as ph_err:
                        logger.warning(f"Placeholder cover also failed: {ph_err}")
                        # Cover is optional — continue without it

                await session.commit()

            # ─── Complete ────────────────────────────────────────────────────
            await session.refresh(podcast)
            from datetime import datetime
            podcast.completed_at = datetime.utcnow()
            await _update_status(session, podcast, PodcastStatus.COMPLETED)

            logger.info(f"Podcast {podcast_id} completed successfully")
            return {"status": "success", "podcast_id": podcast_id}

        except Exception as exc:
            logger.error(f"Podcast {podcast_id} processing failed: {exc}", exc_info=True)
            # Update status to failed
            await _mark_failed(session, podcast_id, str(exc))

            # Retry the task (max 3 times)
            try:
                raise celery_task.retry(exc=exc, countdown=60 * (celery_task.request.retries + 1))
            except Exception:
                return {"status": "failed", "podcast_id": podcast_id, "error": str(exc)}


async def _generate_placeholder_cover(title: str) -> str:
    """Generate a simple placeholder cover image using Pillow"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        # Create upload directory
        upload_dir = Path("uploads/covers")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Create image
        img = Image.new("RGB", (800, 800), color=(79, 70, 229))  # Indigo background
        draw = ImageDraw.Draw(img)

        # Draw gradient-like effect
        for i in range(800):
            alpha = int(255 * (1 - i / 800) * 0.3)
            draw.line([(0, i), (800, i)], fill=(99, 102, 241, alpha))

        # Draw title text
        try:
            font = ImageFont.truetype("arial.ttf", 60)
            small_font = ImageFont.truetype("arial.ttf", 30)
        except Exception:
            font = ImageFont.load_default()
            small_font = font

        # Wrap title
        wrapped = textwrap.fill(title, width=20)
        draw.multiline_text(
            (400, 350),
            wrapped,
            font=font,
            fill="white",
            anchor="mm",
            align="center",
        )

        # Draw "AI PODCAST" label
        draw.text(
            (400, 650),
            "🎙 AI PODCAST",
            font=small_font,
            fill=(199, 210, 254),
            anchor="mm",
        )

        # Save
        cover_filename = f"covers/{uuid.uuid4()}.png"
        cover_path = f"uploads/{cover_filename}"
        img.save(cover_path, "PNG")
        return cover_path

    except Exception as e:
        logger.warning(f"Could not generate placeholder cover: {e}")
        return ""


async def _update_status(
    session: AsyncSession, podcast: Podcast, status: PodcastStatus
):
    """Update podcast status"""
    podcast.status = status
    await session.commit()
    logger.debug(f"Podcast {podcast.id} status -> {status.value}")


async def _mark_failed(session: AsyncSession, podcast_id: str, error: str):
    """Mark podcast as failed"""
    try:
        result = await session.execute(
            select(Podcast).where(Podcast.id == podcast_id)
        )
        podcast = result.scalar_one_or_none()

        if podcast:
            podcast.status = PodcastStatus.FAILED
            podcast.error_message = error[:2000]  # Limit error message length
            await session.commit()
            logger.info(f"Podcast {podcast_id} marked as failed")
    except Exception as e:
        logger.error(f"Failed to mark podcast as failed: {e}")


@shared_task
def cleanup_old_podcasts(days: int = 30):
    """
    Cleanup old podcast files and data

    Args:
        days: Delete podcasts older than this many days
    """
    logger.info(f"Starting cleanup of podcasts older than {days} days")
    return asyncio.run(_cleanup_old_podcasts_async(days))


async def _cleanup_old_podcasts_async(days: int):
    """Async implementation of cleanup"""
    from datetime import datetime, timedelta

    async with async_session() as session:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Find old completed or failed podcasts
        result = await session.execute(
            select(Podcast).where(
                Podcast.status.in_([PodcastStatus.COMPLETED, PodcastStatus.FAILED]),
                Podcast.updated_at < cutoff_date,
            )
        )
        old_podcasts = result.scalars().all()

        deleted_count = 0
        for podcast in old_podcasts:
            # Delete associated files
            for file_attr in ["audio_file", "cover_image"]:
                file_path_str = getattr(podcast, file_attr, None)
                if file_path_str:
                    file_path = Path(str(file_path_str))
                    if file_path.exists():
                        try:
                            os.remove(file_path)
                            logger.debug(f"Deleted file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Could not delete file {file_path}: {e}")

            # Delete from database
            await session.delete(podcast)
            deleted_count += 1

        await session.commit()
        logger.info(f"Cleanup complete: deleted {deleted_count} podcasts")
        return {"deleted_count": deleted_count}
