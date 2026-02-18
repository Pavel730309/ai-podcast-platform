"""
API endpoints for RSS feed generation
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.models import Podcast, PodcastEpisode, PodcastStatus
from app.schemas import RSSFeedResponse
from app.services.rss import RSSGenerator
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rss", tags=["rss"])

rss_generator = RSSGenerator()


@router.get("/podcast/{podcast_id}", response_model=RSSFeedResponse)
async def get_podcast_rss_info(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get RSS feed metadata for a podcast.

    - **podcast_id**: ID of the podcast
    """
    result = await db.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    if podcast.status != PodcastStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Podcast is not completed yet (status: {podcast.status})",
        )

    # Count episodes
    ep_result = await db.execute(
        select(PodcastEpisode).where(PodcastEpisode.podcast_id == podcast_id)
    )
    episodes = ep_result.scalars().all()

    base_url = settings.BASE_URL if hasattr(settings, "BASE_URL") else "http://localhost:8000"
    feed_url = f"{base_url}/api/rss/podcast/{podcast_id}.xml"

    # Save rss_feed URL to podcast if not set
    if not podcast.rss_feed:
        podcast.rss_feed = feed_url
        await db.commit()

    return RSSFeedResponse(
        feed_url=feed_url,
        podcast_id=podcast_id,
        title=podcast.title,
        description=podcast.description or "",
        episode_count=len(episodes) if episodes else 1,
        last_updated=podcast.updated_at,
    )


@router.get("/podcast/{podcast_id}.xml")
async def get_podcast_rss_xml(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get RSS feed XML for a podcast.

    - **podcast_id**: ID of the podcast
    """
    result = await db.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    if podcast.status != PodcastStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Podcast is not completed yet (status: {podcast.status})",
        )

    base_url = settings.BASE_URL if hasattr(settings, "BASE_URL") else "http://localhost:8000"

    # Fetch episodes
    ep_result = await db.execute(
        select(PodcastEpisode).where(PodcastEpisode.podcast_id == podcast_id)
    )
    episodes = ep_result.scalars().all()

    try:
        if episodes:
            xml_bytes = rss_generator.generate_podcast_feed(
                podcast=podcast,
                episodes=list(episodes),
                base_url=base_url,
            )
        else:
            # Treat the podcast itself as a single episode
            episode_data = []
            if podcast.audio_file:
                episode_data.append(
                    {
                        "id": podcast.id,
                        "title": podcast.title,
                        "description": podcast.description or "",
                        "audio_file": podcast.audio_file,
                        "duration": podcast.duration_seconds or 0,
                        "pub_date": podcast.completed_at or podcast.created_at,
                    }
                )
            xml_bytes = rss_generator.generate_simple_feed(
                title=podcast.title,
                description=podcast.description or "",
                episodes=episode_data,
                base_url=base_url,
            )

        if isinstance(xml_bytes, str):
            xml_bytes = xml_bytes.encode("utf-8")

        return Response(content=xml_bytes, media_type="application/rss+xml; charset=utf-8")

    except Exception as e:
        logger.error(f"Error generating RSS XML for podcast {podcast_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating RSS feed: {str(e)}")


@router.get("/validate/{podcast_id}")
async def validate_podcast_rss(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate RSS feed for a podcast.

    - **podcast_id**: ID of the podcast
    """
    result = await db.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    base_url = settings.BASE_URL if hasattr(settings, "BASE_URL") else "http://localhost:8000"
    feed_url = f"{base_url}/api/rss/podcast/{podcast_id}.xml"

    issues = []
    if not podcast.title:
        issues.append("Missing podcast title")
    if not podcast.audio_file:
        issues.append("Missing audio file")
    if podcast.status != PodcastStatus.COMPLETED:
        issues.append(f"Podcast status is '{podcast.status}', expected 'completed'")

    return {
        "valid": len(issues) == 0,
        "feed_url": feed_url,
        "podcast_id": podcast_id,
        "issues": issues,
    }
