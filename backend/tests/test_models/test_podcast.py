"""
Unit tests for Database Models
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Podcast, PodcastParticipant, PodcastStatus, PodcastStyle


class TestPodcastModel:
    """Test Podcast model"""

    @pytest.mark.asyncio
    async def test_create_podcast(self, db_session: AsyncSession):
        """Test creating a podcast"""
        # Arrange & Act
        podcast = Podcast(
            title="Test Podcast",
            style=PodcastStyle.ENTERTAINMENT,
            num_participants=2,
            source_type="text",
            status=PodcastStatus.PENDING,
        )
        db_session.add(podcast)
        await db_session.commit()
        await db_session.refresh(podcast)

        # Assert
        assert podcast.id is not None
        assert podcast.title == "Test Podcast"
        assert podcast.status == PodcastStatus.PENDING
        assert podcast.created_at is not None
        assert podcast.updated_at is not None

    @pytest.mark.asyncio
    async def test_podcast_status_update(self, db_session: AsyncSession):
        """Test updating podcast status"""
        # Arrange
        podcast = Podcast(
            title="Test Podcast",
            style=PodcastStyle.ENTERTAINMENT,
            num_participants=2,
            source_type="text",
            status=PodcastStatus.PENDING,
        )
        db_session.add(podcast)
        await db_session.commit()

        # Act
        podcast.status = PodcastStatus.COMPLETED
        podcast.completed_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(podcast)

        # Assert
        assert podcast.status == PodcastStatus.COMPLETED
        assert podcast.completed_at is not None

    @pytest.mark.asyncio
    async def test_podcast_participants_relationship(self, db_session: AsyncSession):
        """Test podcast participants relationship"""
        # Arrange
        podcast = Podcast(
            title="Test Podcast",
            style=PodcastStyle.ENTERTAINMENT,
            num_participants=2,
            source_type="text",
        )
        db_session.add(podcast)
        await db_session.commit()
        await db_session.refresh(podcast)

        participant = PodcastParticipant(
            podcast_id=podcast.id,
            name="Test Host",
            role="host",
            voice_provider="openai",
            voice_id="alloy",
        )
        db_session.add(participant)
        await db_session.commit()

        # Act & Assert
        from sqlalchemy import select

        result = await db_session.execute(
            select(PodcastParticipant).where(
                PodcastParticipant.podcast_id == podcast.id
            )
        )
        saved_participant = result.scalar_one()

        assert saved_participant.name == "Test Host"
        assert saved_participant.role == "host"


class TestPodcastStatus:
    """Test PodcastStatus enum"""

    def test_status_values(self):
        """Test status enum values"""
        assert PodcastStatus.PENDING.value == "pending"
        assert PodcastStatus.EXTRACTING_TEXT.value == "extracting_text"
        assert PodcastStatus.GENERATING_SCENARIO.value == "generating_scenario"
        assert PodcastStatus.SYNTHESIZING_SPEECH.value == "synthesizing_speech"
        assert PodcastStatus.PROCESSING_AUDIO.value == "processing_audio"
        assert PodcastStatus.GENERATING_COVER.value == "generating_cover"
        assert PodcastStatus.COMPLETED.value == "completed"
        assert PodcastStatus.FAILED.value == "failed"


class TestPodcastStyle:
    """Test PodcastStyle enum"""

    def test_style_values(self):
        """Test style enum values"""
        assert PodcastStyle.ACADEMIC.value == "academic"
        assert PodcastStyle.ENTERTAINMENT.value == "entertainment"
        assert PodcastStyle.BUSINESS.value == "business"
