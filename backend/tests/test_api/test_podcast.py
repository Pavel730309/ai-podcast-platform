"""
Unit tests for Podcast API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Podcast, PodcastStatus, PodcastStyle


class TestPodcastEndpoints:
    """Test podcast API endpoints"""

    def test_create_podcast(self, client: TestClient, db_session: AsyncSession):
        """Test creating a new podcast"""
        # Arrange
        podcast_data = {
            "title": "Test Podcast",
            "style": "entertainment",
            "num_participants": 2,
            "source_type": "text",
            "source_text": "This is a test podcast content.",
            "participants": [
                {
                    "name": "Host",
                    "role": "host",
                    "voice_provider": "openai",
                    "voice_id": "alloy",
                },
                {
                    "name": "Guest",
                    "role": "expert",
                    "voice_provider": "openai",
                    "voice_id": "echo",
                },
            ],
        }

        # Act
        response = client.post("/api/podcasts", json=podcast_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Podcast"
        assert data["style"] == "entertainment"
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_podcast_validation_error(self, client: TestClient):
        """Test creating a podcast with invalid data"""
        # Arrange - missing required fields
        podcast_data = {"style": "entertainment", "num_participants": 2}

        # Act
        response = client.post("/api/podcasts", json=podcast_data)

        # Assert
        assert response.status_code == 422

    def test_list_podcasts(self, client: TestClient, db_session: AsyncSession):
        """Test listing podcasts"""
        # Arrange - Create some test podcasts
        for i in range(3):
            podcast = Podcast(
                title=f"Test Podcast {i}",
                style=PodcastStyle.ENTERTAINMENT,
                num_participants=2,
                source_type="text",
                status=PodcastStatus.COMPLETED,
            )
            db_session.add(podcast)

        # Commit to save
        import asyncio

        asyncio.run(db_session.commit())

        # Act
        response = client.get("/api/podcasts")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_podcast(self, client: TestClient, db_session: AsyncSession):
        """Test getting a specific podcast"""
        # Arrange - Create a podcast
        podcast = Podcast(
            title="Test Podcast",
            style=PodcastStyle.ENTERTAINMENT,
            num_participants=2,
            source_type="text",
            status=PodcastStatus.COMPLETED,
        )
        db_session.add(podcast)
        import asyncio

        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(podcast))

        # Act
        response = client.get(f"/api/podcasts/{podcast.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Podcast"
        assert "id" in data

    def test_get_podcast_not_found(self, client: TestClient):
        """Test getting a non-existent podcast"""
        # Act
        response = client.get("/api/podcasts/non-existent-id")

        # Assert
        assert response.status_code == 404

    def test_update_podcast(self, client: TestClient, db_session: AsyncSession):
        """Test updating a podcast"""
        # Arrange - Create a podcast
        podcast = Podcast(
            title="Original Title",
            style=PodcastStyle.ENTERTAINMENT,
            num_participants=2,
            source_type="text",
        )
        db_session.add(podcast)
        import asyncio

        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(podcast))

        # Act
        update_data = {"title": "Updated Title"}
        response = client.patch(f"/api/podcasts/{podcast.id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_delete_podcast(self, client: TestClient, db_session: AsyncSession):
        """Test deleting a podcast"""
        # Arrange - Create a podcast
        podcast = Podcast(
            title="To Delete",
            style=PodcastStyle.ENTERTAINMENT,
            num_participants=2,
            source_type="text",
        )
        db_session.add(podcast)
        import asyncio

        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(podcast))

        # Act
        response = client.delete(f"/api/podcasts/{podcast.id}")

        # Assert
        assert response.status_code == 200

        # Verify deletion
        get_response = client.get(f"/api/podcasts/{podcast.id}")
        assert get_response.status_code == 404

    def test_get_podcast_progress(self, client: TestClient, db_session: AsyncSession):
        """Test getting podcast progress"""
        # Arrange - Create a podcast
        podcast = Podcast(
            title="Test Podcast",
            style=PodcastStyle.ENTERTAINMENT,
            num_participants=2,
            source_type="text",
            status=PodcastStatus.GENERATING_SCENARIO,
        )
        db_session.add(podcast)
        import asyncio

        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(podcast))

        # Act
        response = client.get(f"/api/podcasts/{podcast.id}/progress")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "progress_percent" in data
        assert "current_step" in data
        assert data["podcast_id"] == str(podcast.id)
