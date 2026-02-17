"""
TTS service for managing multiple providers
"""

from typing import Optional, List, Dict
import hashlib
from pathlib import Path
import os

from app.services.tts.base_provider import BaseTTSProvider, Voice, TTSResult
from app.services.tts.openai_provider import OpenAITTSProvider
from app.services.tts.elevenlabs_provider import ElevenLabsProvider
from app.services.tts.google_provider import GoogleTTSProvider
from app.services.tts.kie_provider import KIEProvider
from app.config import settings


class TTSService:
    """Service for managing TTS operations with multiple providers"""

    def __init__(self, cache_dir: str = "cache/tts"):
        self.providers: Dict[str, BaseTTSProvider] = {}
        self.cache_dir = Path(cache_dir)
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available TTS providers"""
        # Register OpenAI provider
        self.providers["openai"] = OpenAITTSProvider()

        # Register ElevenLabs provider
        self.providers["elevenlabs"] = ElevenLabsProvider()

        # Register Google Cloud provider
        self.providers["google"] = GoogleTTSProvider()

        # Register KIE.ai provider
        self.providers["kie"] = KIEProvider()

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def register_provider(self, name: str, provider: BaseTTSProvider):
        """Register a new TTS provider"""
        self.providers[name] = provider

    async def synthesize(
        self,
        text: str,
        voice_id: str,
        provider: str = "openai",
        speed: float = 1.0,
        use_cache: bool = True,
        use_fallback: bool = True,
        **kwargs,
    ) -> TTSResult:
        """
        Synthesize speech from text with optional fallback

        Args:
            text: Text to synthesize
            voice_id: Voice identifier
            provider: Primary TTS provider to use
            speed: Speech speed
            use_cache: Whether to use cached results
            use_fallback: Whether to try other providers on failure
            **kwargs: Additional provider-specific parameters

        Returns:
            TTSResult with audio data
        """
        # Get cache key
        cache_key = self._get_cache_key(text, voice_id, provider, speed)

        # Check cache first
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

        # Try primary provider
        tts_provider = self.providers.get(provider)
        if tts_provider and await tts_provider.is_available():
            result = await tts_provider.synthesize(
                text=text, voice_id=voice_id, speed=speed, **kwargs
            )

            if not result.error:
                # Cache result if successful
                if use_cache:
                    self._save_to_cache(cache_key, result)
                return result

            # If primary fails and fallback is disabled, return error
            if not use_fallback:
                return result

        # Try fallback providers
        if use_fallback:
            for fallback_name, fallback_provider in self.providers.items():
                if fallback_name == provider:
                    continue

                if await fallback_provider.is_available():
                    # Use a generic voice for fallback
                    fallback_voice = self._get_fallback_voice(fallback_name)

                    result = await fallback_provider.synthesize(
                        text=text, voice_id=fallback_voice, speed=speed, **kwargs
                    )

                    if not result.error:
                        return result

        # All providers failed
        return TTSResult(
            audio_data=b"",
            duration_seconds=0,
            provider=provider,
            voice_id=voice_id,
            error=f"All TTS providers failed for voice '{voice_id}'",
        )

    def _get_fallback_voice(self, provider: str) -> str:
        """Get a default voice for fallback provider"""
        fallback_voices = {
            "openai": "alloy",
            "elevenlabs": "AZnzlk1XvdvUeBnXmlld",  # Domi
            "google": "en-US-Neural2-C",
            "kie": "neutral",
        }
        return fallback_voices.get(provider, "alloy")

    async def get_voices(
        self, provider: Optional[str] = None, language: Optional[str] = None
    ) -> List[Voice]:
        """
        Get available voices

        Args:
            provider: Filter by provider (optional)
            language: Filter by language (optional)

        Returns:
            List of available voices
        """
        voices = []

        if provider:
            tts_provider = self.providers.get(provider)
            if tts_provider:
                voices = await tts_provider.get_voices(language)
        else:
            for tts_provider in self.providers.values():
                provider_voices = await tts_provider.get_voices(language)
                voices.extend(provider_voices)

        return voices

    def get_available_providers(self) -> List[str]:
        """Get list of available TTS providers"""
        return list(self.providers.keys())

    def _get_cache_key(
        self, text: str, voice_id: str, provider: str, speed: float
    ) -> str:
        """Generate cache key for TTS request"""
        content = f"{text}:{voice_id}:{provider}:{speed}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[TTSResult]:
        """Get cached TTS result"""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        meta_file = self.cache_dir / f"{cache_key}.meta"

        if cache_file.exists() and meta_file.exists():
            try:
                # Read audio data
                with open(cache_file, "rb") as f:
                    audio_data = f.read()

                # Read metadata
                with open(meta_file, "r") as f:
                    lines = f.read().strip().split("\n")
                    if len(lines) >= 4:
                        return TTSResult(
                            audio_data=audio_data,
                            duration_seconds=float(lines[0]),
                            provider=lines[1],
                            voice_id=lines[2],
                            format=lines[3],
                        )
            except Exception:
                pass

        return None

    def _save_to_cache(self, cache_key: str, result: TTSResult):
        """Save TTS result to cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.mp3"
            meta_file = self.cache_dir / f"{cache_key}.meta"

            # Save audio data
            with open(cache_file, "wb") as f:
                f.write(result.audio_data)

            # Save metadata
            with open(meta_file, "w") as f:
                f.write(f"{result.duration_seconds}\n")
                f.write(f"{result.provider}\n")
                f.write(f"{result.voice_id}\n")
                f.write(f"{result.format}\n")
        except Exception:
            pass

    def clear_cache(self):
        """Clear TTS cache"""
        for file in self.cache_dir.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass

    def get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total_size = 0
        for file in self.cache_dir.glob("*"):
            total_size += file.stat().st_size
        return total_size
