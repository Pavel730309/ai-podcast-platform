"""
Health check endpoint for the backend
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.database import engine
from app.config import settings
import asyncio

async def check_database():
    """Check database connectivity"""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "service": "database"}
    except Exception as e:
        return {"status": "unhealthy", "service": "database", "error": str(e)}

async def check_redis():
    """Check Redis connectivity"""
    try:
        import redis.asyncio as redis
        client = redis.from_url(settings.REDIS_URL)
        await client.ping()
        await client.close()
        return {"status": "healthy", "service": "redis"}
    except Exception as e:
        return {"status": "unhealthy", "service": "redis", "error": str(e)}

async def check_tts_services():
    """Check TTS service availability"""
    try:
        # Check if we can import TTS providers
        from app.services.tts import TTSService
        service = TTSService()
        providers = service.get_available_providers()
        return {
            "status": "healthy" if providers else "unhealthy", 
            "service": "tts",
            "providers": providers
        }
    except Exception as e:
        return {"status": "unhealthy", "service": "tts", "error": str(e)}

async def check_audio_services():
    """Check audio processing service availability"""
    try:
        from app.services.audio import AudioProcessor
        processor = AudioProcessor()
        return {"status": "healthy", "service": "audio_processing"}
    except Exception as e:
        return {"status": "unhealthy", "service": "audio_processing", "error": str(e)}

async def check_image_services():
    """Check image generation service availability"""
    try:
        from app.services.image_generation import ImageGenerator
        generator = ImageGenerator()
        return {"status": "healthy", "service": "image_generation"}
    except Exception as e:
        return {"status": "unhealthy", "service": "image_generation", "error": str(e)}

async def health_check():
    """Perform comprehensive health check"""
    # Run all checks concurrently
    tasks = [
        check_database(),
        check_redis(),
        check_tts_services(),
        check_audio_services(),
        check_image_services()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    health_status = "healthy"
    services = []
    
    for result in results:
        if isinstance(result, Exception):
            services.append({
                "status": "unhealthy",
                "service": "unknown",
                "error": str(result)
            })
            health_status = "unhealthy"
        else:
            services.append(result)
            if result["status"] == "unhealthy":
                health_status = "unhealthy"
    
    return {
        "status": health_status,
        "timestamp": "2026-02-16T16:00:00Z",
        "services": services
    }

# Add health check to main app
async def setup_health_check(app: FastAPI):
    """Setup health check endpoint"""
    @app.get("/health", response_model=dict)
    async def health_endpoint():
        return await health_check()
    
    return app