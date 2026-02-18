"""
API endpoints for podcast export
"""
import io
import logging
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.models import Podcast, PodcastStatus
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["export"])


def _get_base_url() -> str:
    return settings.BASE_URL if hasattr(settings, "BASE_URL") else "http://localhost:8000"


async def _get_completed_podcast(podcast_id: str, db: AsyncSession) -> Podcast:
    """Helper: fetch podcast and verify it is completed."""
    result = await db.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    if podcast.status != PodcastStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Podcast is not completed yet (status: {podcast.status})",
        )
    return podcast


@router.get("/podcast/{podcast_id}/audio")
async def download_audio(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download the podcast audio file (MP3).

    - **podcast_id**: ID of the podcast
    """
    podcast = await _get_completed_podcast(podcast_id, db)

    if not podcast.audio_file:
        raise HTTPException(status_code=404, detail="Audio file not available")

    audio_path = Path(podcast.audio_file)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found on disk")

    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in podcast.title)
    filename = f"{safe_title}.mp3"

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=filename,
    )


@router.get("/podcast/{podcast_id}/cover")
async def download_cover(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download the podcast cover image (PNG).

    - **podcast_id**: ID of the podcast
    """
    podcast = await _get_completed_podcast(podcast_id, db)

    if not podcast.cover_image:
        raise HTTPException(status_code=404, detail="Cover image not available")

    cover_path = Path(podcast.cover_image)
    if not cover_path.exists():
        raise HTTPException(status_code=404, detail="Cover image not found on disk")

    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in podcast.title)
    filename = f"{safe_title}_cover.png"

    return FileResponse(
        path=str(cover_path),
        media_type="image/png",
        filename=filename,
    )


@router.get("/podcast/{podcast_id}/zip")
async def download_zip(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download a ZIP archive containing audio, cover image, and RSS feed XML.

    - **podcast_id**: ID of the podcast
    """
    podcast = await _get_completed_podcast(podcast_id, db)

    base_url = _get_base_url()
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in podcast.title)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Add audio file
        if podcast.audio_file:
            audio_path = Path(podcast.audio_file)
            if audio_path.exists():
                zf.write(audio_path, arcname=f"{safe_title}.mp3")
            else:
                logger.warning(f"Audio file not found on disk: {audio_path}")

        # Add cover image
        if podcast.cover_image:
            cover_path = Path(podcast.cover_image)
            if cover_path.exists():
                zf.write(cover_path, arcname=f"{safe_title}_cover.png")
            else:
                logger.warning(f"Cover image not found on disk: {cover_path}")

        # Add RSS feed XML
        rss_xml = _build_simple_rss(podcast, base_url)
        zf.writestr("feed.rss", rss_xml)

        # Add metadata JSON
        import json
        metadata = {
            "id": podcast.id,
            "title": podcast.title,
            "description": podcast.description or "",
            "style": podcast.style.value if hasattr(podcast.style, "value") else str(podcast.style),
            "duration_seconds": podcast.duration_seconds,
            "created_at": podcast.created_at.isoformat() if podcast.created_at else None,
            "completed_at": podcast.completed_at.isoformat() if podcast.completed_at else None,
            "rss_feed": f"{base_url}/api/rss/podcast/{podcast.id}.xml",
        }
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}.zip"',
        },
    )


@router.get("/podcast/{podcast_id}/rss")
async def download_rss(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download the RSS feed XML file for the podcast.

    - **podcast_id**: ID of the podcast
    """
    podcast = await _get_completed_podcast(podcast_id, db)
    base_url = _get_base_url()
    rss_xml = _build_simple_rss(podcast, base_url)

    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in podcast.title)
    return Response(
        content=rss_xml.encode("utf-8"),
        media_type="application/rss+xml; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}.rss"'},
    )


@router.get("/podcast/{podcast_id}/info")
async def get_export_info(
    podcast_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get available export options for a podcast.

    - **podcast_id**: ID of the podcast
    """
    podcast = await _get_completed_podcast(podcast_id, db)
    base_url = _get_base_url()

    exports = []

    if podcast.audio_file and Path(podcast.audio_file).exists():
        exports.append(
            {
                "type": "audio",
                "format": "mp3",
                "url": f"{base_url}/api/export/podcast/{podcast_id}/audio",
                "description": "Podcast audio (MP3)",
            }
        )

    if podcast.cover_image and Path(podcast.cover_image).exists():
        exports.append(
            {
                "type": "cover",
                "format": "png",
                "url": f"{base_url}/api/export/podcast/{podcast_id}/cover",
                "description": "Cover image (PNG)",
            }
        )

    exports.append(
        {
            "type": "rss",
            "format": "xml",
            "url": f"{base_url}/api/rss/podcast/{podcast_id}.xml",
            "description": "RSS feed (XML) — for Spotify, Apple Podcasts, etc.",
        }
    )

    exports.append(
        {
            "type": "zip",
            "format": "zip",
            "url": f"{base_url}/api/export/podcast/{podcast_id}/zip",
            "description": "Full archive (audio + cover + RSS + metadata)",
        }
    )

    return {
        "podcast_id": podcast_id,
        "title": podcast.title,
        "available_exports": exports,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_simple_rss(podcast: Podcast, base_url: str) -> str:
    """Build a minimal RSS 2.0 / iTunes feed for a single-episode podcast."""
    audio_url = (
        f"{base_url}{podcast.audio_file}"
        if podcast.audio_file and not podcast.audio_file.startswith("http")
        else (podcast.audio_file or "")
    )
    cover_url = (
        f"{base_url}{podcast.cover_image}"
        if podcast.cover_image and not podcast.cover_image.startswith("http")
        else (podcast.cover_image or "")
    )
    pub_date = (podcast.completed_at or podcast.created_at).strftime(
        "%a, %d %b %Y %H:%M:%S +0000"
    )
    duration = str(podcast.duration_seconds or 0)
    description = (podcast.description or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    title = podcast.title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{title}</title>
    <description>{description}</description>
    <link>{base_url}/podcast/{podcast.id}</link>
    <language>ru</language>
    <pubDate>{pub_date}</pubDate>
    <lastBuildDate>{pub_date}</lastBuildDate>
    <itunes:author>AI Podcast Platform</itunes:author>
    <itunes:summary>{description}</itunes:summary>
    <itunes:explicit>no</itunes:explicit>
    <itunes:category text="Technology"/>
    {f'<itunes:image href="{cover_url}"/>' if cover_url else ''}
    {f'<image><url>{cover_url}</url><title>{title}</title><link>{base_url}</link></image>' if cover_url else ''}
    <item>
      <title>{title}</title>
      <description>{description}</description>
      <pubDate>{pub_date}</pubDate>
      <guid isPermaLink="false">{podcast.id}</guid>
      {f'<enclosure url="{audio_url}" length="0" type="audio/mpeg"/>' if audio_url else ''}
      <itunes:duration>{duration}</itunes:duration>
      <itunes:explicit>no</itunes:explicit>
      <itunes:episode>1</itunes:episode>
    </item>
  </channel>
</rss>"""
