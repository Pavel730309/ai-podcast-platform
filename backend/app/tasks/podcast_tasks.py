"""
Podcast processing tasks for Celery
"""

import asyncio
from typing import Optional
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models import Podcast, PodcastStatus
from app.services.text_extraction.extraction_service import TextExtractionService
from app.services.scenario.scenario_service import ScenarioService
from app.services.tts.tts_service import TTSService
from app.services.audio.audio_processor import AudioProcessor


@shared_task(bind=True, max_retries=3)
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
    # Run async code in Celery task
    return asyncio.run(_process_podcast_async(self, podcast_id))


async def _process_podcast_async(celery_task, podcast_id: str):
    """Async implementation of podcast processing"""
    async with async_session() as session:
        podcast: Optional[Podcast] = None
        try:
            # Get podcast
            from sqlalchemy import select

            result = await session.execute(
                select(Podcast).where(Podcast.id == podcast_id)
            )
            podcast = result.scalar_one_or_none()

            if not podcast:
                raise ValueError(f"Podcast {podcast_id} not found")

            # Stage 1: Extract text (if not already done)
            current_status = str(podcast.status) if podcast.status else None
            if current_status == PodcastStatus.PENDING.value:
                await _update_status(session, podcast, PodcastStatus.EXTRACTING_TEXT)
                await session.refresh(podcast)

                source_url = str(podcast.source_url) if podcast.source_url else None
                if source_url:
                    extraction_service = TextExtractionService()
                    extraction_result = await extraction_service.extract_from_url(
                        source_url
                    )
                    if extraction_result.text:
                        podcast.extracted_text = extraction_result.text
                        await session.commit()

            # Stage 2: Generate scenario
            await session.refresh(podcast)
            current_status = str(podcast.status) if podcast.status else None
            if current_status == PodcastStatus.EXTRACTING_TEXT.value:
                await _update_status(
                    session, podcast, PodcastStatus.GENERATING_SCENARIO
                )
                await session.refresh(podcast)

                extracted_text = (
                    str(podcast.extracted_text) if podcast.extracted_text else None
                )
                if extracted_text:
                    scenario_service = ScenarioService()
                    style_value = (
                        str(podcast.style.value) if podcast.style else "entertainment"
                    )
                    num_participants = (
                        int(podcast.num_participants) if podcast.num_participants else 2
                    )

                    scenario_result = await scenario_service.generate_scenario(
                        text=extracted_text,
                        style=style_value,
                        num_participants=num_participants,
                    )

                    if scenario_result.error:
                        raise Exception(
                            f"Scenario generation failed: {scenario_result.error}"
                        )

                    podcast.scenario = scenario_service.scenario_to_json(
                        scenario_result
                    )
                    await session.commit()

            # Stage 3: Synthesize speech
            await session.refresh(podcast)
            current_status = str(podcast.status) if podcast.status else None
            if current_status == PodcastStatus.GENERATING_SCENARIO.value:
                await _update_status(
                    session, podcast, PodcastStatus.SYNTHESIZING_SPEECH
                )
                await session.refresh(podcast)

                # TODO: Implement speech synthesis from scenario
                # This would parse the scenario JSON and synthesize each dialogue line
                scenario_text = str(podcast.scenario) if podcast.scenario else None
                if scenario_text:
                    # Parse scenario and synthesize
                    pass

            # Stage 4: Process audio
            await session.refresh(podcast)
            current_status = str(podcast.status) if podcast.status else None
            if current_status == PodcastStatus.SYNTHESIZING_SPEECH.value:
                await _update_status(session, podcast, PodcastStatus.PROCESSING_AUDIO)
                await session.refresh(podcast)
                # TODO: Audio processing logic - mix speech with background music

            # Stage 5: Generate cover
            await session.refresh(podcast)
            current_status = str(podcast.status) if podcast.status else None
            if current_status == PodcastStatus.PROCESSING_AUDIO.value:
                await _update_status(session, podcast, PodcastStatus.GENERATING_COVER)
                await session.refresh(podcast)
                # TODO: Cover generation logic

            # Complete
            await session.refresh(podcast)
            await _update_status(session, podcast, PodcastStatus.COMPLETED)

            return {"status": "success", "podcast_id": podcast_id}

        except Exception as exc:
            # Update status to failed
            await _mark_failed(session, podcast_id, str(exc))

            # Retry the task
            raise celery_task.retry(exc=exc, countdown=60)


async def _update_status(
    session: AsyncSession, podcast: Podcast, status: PodcastStatus
):
    """Update podcast status"""
    podcast.status = status
    await session.commit()


async def _mark_failed(session: AsyncSession, podcast_id: str, error: str):
    """Mark podcast as failed"""
    from sqlalchemy import select

    result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if podcast:
        podcast.status = PodcastStatus.FAILED
        podcast.error_message = error
        await session.commit()


@shared_task
def cleanup_old_podcasts(days: int = 30):
    """
    Cleanup old podcast files and data

    Args:
        days: Delete podcasts older than this many days
    """
    return asyncio.run(_cleanup_old_podcasts_async(days))


async def _cleanup_old_podcasts_async(days: int):
    """Async implementation of cleanup"""
    from datetime import datetime, timedelta
    from sqlalchemy import select

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
            audio_file = str(podcast.audio_file) if podcast.audio_file else None
            cover_image = str(podcast.cover_image) if podcast.cover_image else None

            if audio_file:
                # TODO: Remove file from storage
                pass
            if cover_image:
                # TODO: Remove image from storage
                pass

            # Delete from database
            await session.delete(podcast)
            deleted_count += 1

        await session.commit()

        return {"deleted_count": deleted_count}
