"""
API router configuration
"""
from fastapi import APIRouter

from app.api.endpoints import text, podcast, scenario, tts, audio, image, rss, export

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(text.router)
api_router.include_router(podcast.router)
api_router.include_router(scenario.router)
api_router.include_router(tts.router)
api_router.include_router(audio.router)
api_router.include_router(image.router)
api_router.include_router(rss.router)
api_router.include_router(export.router)
