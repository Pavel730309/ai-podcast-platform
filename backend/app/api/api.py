"""
API router configuration
"""
from fastapi import APIRouter

from app.api.endpoints import text, podcast, scenario, tts, audio, image, rss, export, auth

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router)

# Core endpoints
api_router.include_router(text.router)
api_router.include_router(podcast.router)
api_router.include_router(scenario.router)
api_router.include_router(tts.router)
api_router.include_router(audio.router)
api_router.include_router(image.router)
api_router.include_router(rss.router)
api_router.include_router(export.router)
