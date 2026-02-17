"""
Unit tests for TTS services
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

from app.services.tts.tts_service import TTSService
from app.services.tts.openai_provider import OpenAITTSProvider
from app.services.tts.base_provider import Voice, TTSResult, VoiceGender


class TestTTSService:
    """Test TTS service"""

    @pytest.fixture
    def tts_service(self, tmp_path):
        """Create TTS service with temp cache dir"""
        cache_dir = tmp_path / "tts_cache"
        return TTSService(cache_dir=str(cache_dir))

    @pytest.mark.asyncio
    async def test_synthesize_with_cache(self, tts_service):
        """Test synthesis with caching"""
        # Arrange
        test_audio = b"fake_audio_data"
        mock_result = TTSResult(
            audio_data=test_audio,
            duration_seconds=1.5,
            provider="openai",
            voice_id="alloy",
        )

        # Mock the provider
        mock_provider = AsyncMock()
        mock_provider.is_available.return_value = True
        mock_provider.synthesize.return_value = mock_result

        tts_service.providers["openai"] = mock_provider

        # Act - First call (should use provider)
        result1 = await tts_service.synthesize(
            text="Hello world", voice_id="alloy", provider="openai", use_cache=True
        )

        # Act - Second call (should use cache)
        result2 = await tts_service.synthesize(
            text="Hello world", voice_id="alloy", provider="openai", use_cache=True
        )

        # Assert
        assert result1.audio_data == test_audio
        assert result2.audio_data == test_audio
        # Provider should only be called once due to caching
        mock_provider.synthesize.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesize_provider_fallback(self, tts_service):
        """Test fallback when primary provider fails"""
        # Arrange
        # Primary provider fails
        mock_primary = AsyncMock()
        mock_primary.is_available.return_value = True
        mock_primary.synthesize.return_value = TTSResult(
            audio_data=b"",
            duration_seconds=0,
            provider="openai",
            voice_id="alloy",
            error="Primary failed",
        )

        # Fallback provider succeeds
        mock_fallback = AsyncMock()
        mock_fallback.is_available.return_value = True
        mock_fallback.synthesize.return_value = TTSResult(
            audio_data=b"fallback_audio",
            duration_seconds=1.5,
            provider="elevenlabs",
            voice_id="fallback_voice",
        )

        tts_service.providers["openai"] = mock_primary
        tts_service.providers["elevenlabs"] = mock_fallback

        # Act
        result = await tts_service.synthesize(
            text="Hello world", voice_id="alloy", provider="openai", use_fallback=True
        )

        # Assert
        assert result.audio_data == b"fallback_audio"
        assert result.provider == "elevenlabs"

    @pytest.mark.asyncio
    async def test_synthesize_provider_not_found(self, tts_service):
        """Test when provider doesn't exist"""
        # Act
        result = await tts_service.synthesize(
            text="Hello world", voice_id="alloy", provider="nonexistent"
        )

        # Assert
        assert result.error is not None
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_voices(self, tts_service):
        """Test getting available voices"""
        # Arrange
        mock_voices = [
            Voice(
                id="voice1", name="Voice 1", provider="openai", gender=VoiceGender.MALE
            ),
            Voice(
                id="voice2",
                name="Voice 2",
                provider="openai",
                gender=VoiceGender.FEMALE,
            ),
        ]

        mock_provider = AsyncMock()
        mock_provider.get_voices.return_value = mock_voices
        tts_service.providers["openai"] = mock_provider

        # Act
        voices = await tts_service.get_voices(provider="openai")

        # Assert
        assert len(voices) == 2
        assert voices[0].id == "voice1"

    def test_get_cache_key(self, tts_service):
        """Test cache key generation"""
        # Act
        key1 = tts_service._get_cache_key("Hello", "alloy", "openai", 1.0)
        key2 = tts_service._get_cache_key("Hello", "alloy", "openai", 1.0)
        key3 = tts_service._get_cache_key("World", "alloy", "openai", 1.0)

        # Assert
        assert key1 == key2  # Same input = same key
        assert key1 != key3  # Different input = different key
        assert len(key1) == 32  # MD5 hash length

    def test_save_and_get_from_cache(self, tts_service):
        """Test saving and retrieving from cache"""
        # Arrange
        cache_key = "test_key"
        result = TTSResult(
            audio_data=b"test_audio",
            duration_seconds=2.0,
            provider="openai",
            voice_id="alloy",
        )

        # Act - Save to cache
        tts_service._save_to_cache(cache_key, result)

        # Act - Retrieve from cache
        cached = tts_service._get_from_cache(cache_key)

        # Assert
        assert cached is not None
        assert cached.audio_data == b"test_audio"
        assert cached.duration_seconds == 2.0

    def test_clear_cache(self, tts_service):
        """Test clearing cache"""
        # Arrange - Add some cached files
        result = TTSResult(
            audio_data=b"test",
            duration_seconds=1.0,
            provider="openai",
            voice_id="alloy",
        )
        tts_service._save_to_cache("key1", result)
        tts_service._save_to_cache("key2", result)

        # Act
        initial_size = tts_service.get_cache_size()
        tts_service.clear_cache()
        final_size = tts_service.get_cache_size()

        # Assert
        assert initial_size > 0
        assert final_size == 0


class TestOpenAITTSProvider:
    """Test OpenAI TTS provider"""

    @pytest.fixture
    def provider(self):
        return OpenAITTSProvider()

    @pytest.mark.asyncio
    async def test_is_available_with_key(self, provider):
        """Test availability when API key is set"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            assert await provider.is_available() is True

    @pytest.mark.asyncio
    async def test_is_available_without_key(self, provider):
        """Test availability when API key is not set"""
        with patch.dict(os.environ, {}, clear=True):
            assert await provider.is_available() is False

    @pytest.mark.asyncio
    async def test_get_voices(self, provider):
        """Test getting available voices"""
        voices = await provider.get_voices()

        # Assert - Should return default voices
        assert len(voices) > 0
        assert all(v.provider == "openai" for v in voices)
        assert all(isinstance(v.gender, VoiceGender) for v in voices)

    @pytest.mark.asyncio
    async def test_get_voices_filtered_by_language(self, provider):
        """Test filtering voices by language"""
        voices = await provider.get_voices(language="en")

        # All voices should be English
        assert all(v.language.startswith("en") for v in voices)

    def test_default_voices_structure(self, provider):
        """Test structure of default voices"""
        voices = provider._get_default_voices()

        # Assert structure
        for voice in voices:
            assert hasattr(voice, "id")
            assert hasattr(voice, "name")
            assert hasattr(voice, "provider")
            assert hasattr(voice, "gender")
            assert hasattr(voice, "language")
            assert voice.provider == "openai"
