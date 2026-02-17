"""
API endpoints for podcast management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json
from datetime import datetime

from app.database import get_session
from app.models import Podcast, PodcastParticipant, PodcastStatus, PodcastStyle
from app.schemas import (
    PodcastCreate,
    PodcastUpdate,
    PodcastResponse,
    PodcastDetailResponse,
    ParticipantResponse,
    ProgressResponse,
    PodcastStyleEnum,
    PodcastStatusEnum,
)
from app.api.endpoints.helpers import (
    podcast_to_response,
    participant_to_response,
    podcast_to_detail_response,
)
from app.tasks.podcast_tasks import process_podcast

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


@router.post("", response_model=PodcastResponse)
async def create_podcast(
    podcast_data: PodcastCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new podcast

    - **title**: Podcast title
    - **description**: Podcast description
    - **style**: Podcast style (academic, entertainment, business)
    - **num_participants**: Number of participants (2-4)
    - **source_type**: Type of source (pdf, docx, url, text)
    - **source_url**: URL if source_type is url
    - **source_text**: Text if source_type is text
    - **participants**: List of participants with voice settings
    """
    # Create podcast
    podcast = Podcast(
        title=podcast_data.title,
        description=podcast_data.description,
        style=PodcastStyle(podcast_data.style.value),
        num_participants=podcast_data.num_participants,
        source_type=podcast_data.source_type.value,
        source_url=podcast_data.source_url,
        status=PodcastStatus.PENDING,
    )

    # Handle source text
    if podcast_data.source_text:
        podcast.extracted_text = podcast_data.source_text

    session.add(podcast)
    await session.commit()
    await session.refresh(podcast)

    # Add participants
    for participant_data in podcast_data.participants:
        participant = PodcastParticipant(
            podcast_id=podcast.id,
            name=participant_data.name,
            role=participant_data.role,
            voice_provider=participant_data.voice_provider,
            voice_id=participant_data.voice_id,
            voice_settings=json.dumps(participant_data.voice_settings.dict())
            if participant_data.voice_settings
            else None,
        )
        session.add(participant)

    await session.commit()

    # Start background processing
    process_podcast.delay(str(podcast.id))

    return podcast_to_response(podcast)


@router.get("", response_model=List[PodcastResponse])
async def list_podcasts(
    skip: int = 0, limit: int = 20, session: AsyncSession = Depends(get_session)
):
    """
    List all podcasts

    - **skip**: Number of podcasts to skip
    - **limit**: Maximum number of podcasts to return
    """
    result = await session.execute(
        select(Podcast).order_by(Podcast.created_at.desc()).offset(skip).limit(limit)
    )
    podcasts = result.scalars().all()

    return [podcast_to_response(p) for p in podcasts]


@router.get("/{podcast_id}", response_model=PodcastDetailResponse)
async def get_podcast(podcast_id: str, session: AsyncSession = Depends(get_session)):
    """
    Get podcast details by ID

    - **podcast_id**: Podcast ID
    """
    result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Get participants
    participants_result = await session.execute(
        select(PodcastParticipant).where(PodcastParticipant.podcast_id == podcast_id)
    )
    participants = participants_result.scalars().all()

    return podcast_to_detail_response(podcast, list(participants))


@router.patch("/{podcast_id}", response_model=PodcastResponse)
async def update_podcast(
    podcast_id: str,
    podcast_data: PodcastUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update podcast details

    - **podcast_id**: Podcast ID
    """
    result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Update fields
    if podcast_data.title is not None:
        podcast.title = podcast_data.title
    if podcast_data.description is not None:
        podcast.description = podcast_data.description
    if podcast_data.style is not None:
        podcast.style = PodcastStyle(podcast_data.style.value)

    podcast.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(podcast)

    return podcast_to_response(podcast)


@router.delete("/{podcast_id}")
async def delete_podcast(podcast_id: str, session: AsyncSession = Depends(get_session)):
    """
    Delete a podcast

    - **podcast_id**: Podcast ID
    """
    result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    await session.delete(podcast)
    await session.commit()

    return {"message": "Podcast deleted successfully"}


@router.get("/{podcast_id}/progress", response_model=ProgressResponse)
async def get_podcast_progress(
    podcast_id: str, session: AsyncSession = Depends(get_session)
):
    """
    Get podcast generation progress

    - **podcast_id**: Podcast ID
    """
    result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Calculate progress percentage
    progress_map = {
        PodcastStatus.PENDING: 0,
        PodcastStatus.EXTRACTING_TEXT: 10,
        PodcastStatus.GENERATING_SCENARIO: 30,
        PodcastStatus.SYNTHESIZING_SPEECH: 50,
        PodcastStatus.PROCESSING_AUDIO: 70,
        PodcastStatus.GENERATING_COVER: 90,
        PodcastStatus.COMPLETED: 100,
        PodcastStatus.FAILED: 0,
    }

    progress_percent = progress_map.get(podcast.status, 0)

    # Map status to step description
    step_map = {
        PodcastStatus.PENDING: "Waiting to start",
        PodcastStatus.EXTRACTING_TEXT: "Extracting text from source",
        PodcastStatus.GENERATING_SCENARIO: "Generating podcast scenario",
        PodcastStatus.SYNTHESIZING_SPEECH: "Synthesizing speech",
        PodcastStatus.PROCESSING_AUDIO: "Processing and mixing audio",
        PodcastStatus.GENERATING_COVER: "Generating cover image",
        PodcastStatus.COMPLETED: "Podcast ready",
        PodcastStatus.FAILED: "Generation failed",
    }

    return ProgressResponse(
        podcast_id=str(podcast.id),
        status=PodcastStatusEnum(str(podcast.status.value)),
        progress_percent=progress_percent,
        current_step=step_map.get(podcast.status, "Unknown"),
        error_message=str(podcast.error_message) if podcast.error_message else None,
        estimated_time_remaining_seconds=None,
    )
