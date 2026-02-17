"""
Health check endpoints for the application
"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse


def setup_health_check(app: FastAPI) -> FastAPI:
    """Add health check endpoints to the application"""

    @app.get("/health", tags=["health"])
    async def health_check():
        """Basic health check endpoint"""
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": "ai-podcast-platform",
                "version": "1.0.0",
            },
        )

    @app.get("/health/ready", tags=["health"])
    async def readiness_check():
        """Readiness probe for Kubernetes"""
        # Check database connection
        try:
            from app.database import async_session

            async with async_session() as session:
                from sqlalchemy import text

                await session.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "database": "disconnected",
                    "error": str(e),
                },
            )

        # Check Redis connection
        try:
            from app.config import settings
            import aioredis

            redis = aioredis.from_url(settings.REDIS_URL)
            await redis.ping()
            await redis.close()
            redis_status = "connected"
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "redis": "disconnected",
                    "error": str(e),
                },
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "database": db_status,
                "redis": redis_status,
            },
        )

    @app.get("/health/live", tags=["health"])
    async def liveness_check():
        """Liveness probe for Kubernetes"""
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "alive"})

    return app
