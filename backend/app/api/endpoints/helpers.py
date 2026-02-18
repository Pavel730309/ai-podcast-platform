"""
Helper functions for converting SQLAlchemy models to Pydantic schemas
"""

from typing import List
from app.models import Podcast, PodcastParticipant, PodcastStatus, PodcastStyle
from app.schemas import (
    PodcastResponse,
    PodcastDetailResponse,
    ParticipantResponse,
    PodcastStyleEnum,
    PodcastStatusEnum,
)


def podcast_to_response(podcast: Podcast) -> PodcastResponse:
    """Convert Podcast model to PodcastResponse schema"""
    return PodcastResponse(
        id=str(podcast.id),
        user_id=str(podcast.user_id) if podcast.user_id else "anonymous",
        title=str(podcast.title) if podcast.title else "",
        description=str(podcast.description) if podcast.description else None,
        style=PodcastStyleEnum(str(podcast.style.value))
        if podcast.style
        else PodcastStyleEnum.ENTERTAINMENT,
        num_participants=int(podcast.num_participants)
        if podcast.num_participants
        else 2,
        status=PodcastStatusEnum(str(podcast.status.value))
        if podcast.status
        else PodcastStatusEnum.PENDING,
        source_type=str(podcast.source_type) if podcast.source_type else "",
        source_file=str(podcast.source_file) if podcast.source_file else None,
        source_url=str(podcast.source_url) if podcast.source_url else None,
        audio_file=str(podcast.audio_file) if podcast.audio_file else None,
        cover_image=str(podcast.cover_image) if podcast.cover_image else None,
        rss_feed=str(podcast.rss_feed) if podcast.rss_feed else None,
        duration_seconds=int(podcast.duration_seconds)
        if podcast.duration_seconds
        else None,
        error_message=str(podcast.error_message) if podcast.error_message else None,
        created_at=podcast.created_at,
        updated_at=podcast.updated_at,
        completed_at=podcast.completed_at,
    )


def participant_to_response(participant: PodcastParticipant) -> ParticipantResponse:
    """Convert PodcastParticipant model to ParticipantResponse schema"""
    import json

    return ParticipantResponse(
        id=str(participant.id),
        name=str(participant.name) if participant.name else "",
        role=str(participant.role) if participant.role else "",
        voice_provider=str(participant.voice_provider)
        if participant.voice_provider
        else "",
        voice_id=str(participant.voice_id) if participant.voice_id else "",
        voice_settings=json.loads(participant.voice_settings)
        if participant.voice_settings
        else None,
    )


def podcast_to_detail_response(
    podcast: Podcast, participants: List[PodcastParticipant]
) -> PodcastDetailResponse:
    """Convert Podcast model to PodcastDetailResponse schema"""
    return PodcastDetailResponse(
        id=str(podcast.id),
        user_id=str(podcast.user_id) if podcast.user_id else "anonymous",
        title=str(podcast.title) if podcast.title else "",
        description=str(podcast.description) if podcast.description else None,
        style=PodcastStyleEnum(str(podcast.style.value))
        if podcast.style
        else PodcastStyleEnum.ENTERTAINMENT,
        num_participants=int(podcast.num_participants)
        if podcast.num_participants
        else 2,
        status=PodcastStatusEnum(str(podcast.status.value))
        if podcast.status
        else PodcastStatusEnum.PENDING,
        source_type=str(podcast.source_type) if podcast.source_type else "",
        source_file=str(podcast.source_file) if podcast.source_file else None,
        source_url=str(podcast.source_url) if podcast.source_url else None,
        audio_file=str(podcast.audio_file) if podcast.audio_file else None,
        cover_image=str(podcast.cover_image) if podcast.cover_image else None,
        rss_feed=str(podcast.rss_feed) if podcast.rss_feed else None,
        duration_seconds=int(podcast.duration_seconds)
        if podcast.duration_seconds
        else None,
        error_message=str(podcast.error_message) if podcast.error_message else None,
        created_at=podcast.created_at,
        updated_at=podcast.updated_at,
        completed_at=podcast.completed_at,
        extracted_text=str(podcast.extracted_text) if podcast.extracted_text else None,
        scenario=str(podcast.scenario) if podcast.scenario else None,
        participants=[participant_to_response(p) for p in participants],
    )
