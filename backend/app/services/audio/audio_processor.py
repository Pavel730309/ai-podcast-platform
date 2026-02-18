"""
Audio processing service for podcast creation
"""

import io
import os
import logging
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from pydub import AudioSegment
from pydub.effects import normalize

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AudioResult:
    """Result of audio processing"""
    file_path: str
    duration_seconds: float
    format: str = "mp3"
    error: Optional[str] = None


class AudioProcessor:
    """Service for audio processing operations"""

    def __init__(self):
        self.supported_formats = ["mp3", "wav", "flac"]
        self.output_dir = Path("uploads/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def mix_audio_with_music(
        self,
        speech_file_path: str,
        music_category: str = "corporate",
        music_volume_db: float = -18.0,
        fade_duration_ms: int = 3000,
        output_dir: str = "uploads/audio",
    ) -> AudioResult:
        """
        Mix speech audio with background music from library.

        Args:
            speech_file_path: Path to the speech audio file
            music_category: Music category (ambient, corporate, electronic, instrumental)
            music_volume_db: Background music volume in dB (negative = quieter)
            fade_duration_ms: Fade in/out duration in ms
            output_dir: Output directory

        Returns:
            AudioResult with path to mixed audio file
        """
        try:
            speech_path = Path(speech_file_path)
            if not speech_path.exists():
                logger.warning(f"Speech file not found: {speech_file_path}")
                return AudioResult(
                    file_path=speech_file_path,
                    duration_seconds=0,
                    error="Speech file not found",
                )

            # Load speech audio
            logger.info(f"Loading speech audio: {speech_file_path}")
            speech_audio = AudioSegment.from_file(str(speech_path))

            # Normalize speech audio
            speech_audio = self._normalize_audio(speech_audio, target_db=-16.0)

            # Try to find background music
            music_audio = self._load_music_from_library(music_category)

            if music_audio is None:
                logger.info("No background music found, saving speech only")
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                output_file = output_path / f"{uuid.uuid4()}.mp3"
                speech_audio.export(str(output_file), format="mp3", bitrate="192k")
                return AudioResult(
                    file_path=str(output_file),
                    duration_seconds=len(speech_audio) / 1000.0,
                )

            # Adjust music volume
            music_audio = music_audio + music_volume_db

            # Loop music if shorter than speech
            speech_len = len(speech_audio)
            if len(music_audio) < speech_len:
                repeats = (speech_len // len(music_audio)) + 2
                music_audio = music_audio * repeats

            # Trim music to speech length + fade
            music_audio = music_audio[:speech_len]

            # Apply fade in/out to music
            fade = min(fade_duration_ms, len(music_audio) // 4)
            music_audio = music_audio.fade_in(fade).fade_out(fade)

            # Mix speech over music
            mixed = speech_audio.overlay(music_audio)

            # Final normalization
            mixed = self._normalize_audio(mixed, target_db=-14.0)

            # Export
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / f"{uuid.uuid4()}.mp3"
            mixed.export(str(output_file), format="mp3", bitrate="192k")

            duration = len(mixed) / 1000.0
            logger.info(f"Audio mixed successfully: {output_file} ({duration:.1f}s)")

            return AudioResult(
                file_path=str(output_file),
                duration_seconds=duration,
            )

        except Exception as e:
            logger.error(f"Error mixing audio: {e}", exc_info=True)
            # Return original file on error
            return AudioResult(
                file_path=speech_file_path,
                duration_seconds=0,
                error=str(e),
            )

    def _normalize_audio(self, audio: AudioSegment, target_db: float = -16.0) -> AudioSegment:
        """Normalize audio to target dB level"""
        try:
            if audio.dBFS == float('-inf'):
                return audio
            change = target_db - audio.dBFS
            # Limit gain change to avoid clipping
            change = max(-20.0, min(20.0, change))
            return audio.apply_gain(change)
        except Exception as e:
            logger.warning(f"Audio normalization failed: {e}")
            return audio

    def _load_music_from_library(self, category: str) -> Optional[AudioSegment]:
        """Load a music track from the local library"""
        music_dirs = [
            Path(f"backend/data/music/{category}"),
            Path(f"data/music/{category}"),
            Path(f"backend/data/music"),
            Path(f"data/music"),
        ]

        for music_dir in music_dirs:
            if music_dir.exists():
                audio_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))
                if audio_files:
                    music_file = audio_files[0]
                    try:
                        logger.info(f"Loading music: {music_file}")
                        return AudioSegment.from_file(str(music_file))
                    except Exception as e:
                        logger.warning(f"Could not load music file {music_file}: {e}")

        logger.info(f"No music files found for category: {category}")
        return None

    async def combine_audio_segments(
        self,
        segments: List[bytes],
        segment_durations: List[float],
        output_format: str = "mp3",
    ) -> bytes:
        """
        Combine multiple audio segments into one

        Args:
            segments: List of audio byte data
            segment_durations: List of durations for each segment
            output_format: Output format (mp3, wav, flac)

        Returns:
            Combined audio as bytes
        """
        temp_files = []
        combined_audio = None

        try:
            for i, (segment_data, duration) in enumerate(
                zip(segments, segment_durations)
            ):
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{output_format}"
                )
                temp_file.write(segment_data)
                temp_file.flush()
                temp_file.close()
                temp_files.append(temp_file.name)

                audio_segment = AudioSegment.from_file(temp_file.name)

                if combined_audio is None:
                    combined_audio = audio_segment
                else:
                    silence = AudioSegment.silent(duration=200)
                    combined_audio += silence + audio_segment

            if combined_audio:
                output_buffer = io.BytesIO()
                combined_audio.export(output_buffer, format=output_format, bitrate="192k")
                return output_buffer.getvalue()
            return b""

        except Exception as e:
            logger.error(f"Error combining audio segments: {e}")
            raise
        finally:
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

    async def add_background_music(
        self,
        speech_audio: bytes,
        music_audio: bytes,
        music_volume_ratio: float = 0.3,
        fade_duration: int = 2000,
    ) -> bytes:
        """Add background music to speech audio"""
        try:
            speech_segment = AudioSegment.from_file(io.BytesIO(speech_audio))
            music_segment = AudioSegment.from_file(io.BytesIO(music_audio))

            # Normalize speech
            speech_segment = self._normalize_audio(speech_segment, -16.0)

            # Adjust music volume
            music_db = -20 + (music_volume_ratio * 10)
            music_segment = music_segment + music_db

            # Loop music if needed
            if len(music_segment) < len(speech_segment):
                repeats = len(speech_segment) // len(music_segment) + 1
                music_segment = music_segment * repeats

            music_segment = music_segment[: len(speech_segment)]
            music_segment = music_segment.fade_in(fade_duration).fade_out(fade_duration)

            mixed_audio = speech_segment.overlay(music_segment)

            output_buffer = io.BytesIO()
            mixed_audio.export(output_buffer, format="mp3", bitrate="192k")
            return output_buffer.getvalue()

        except Exception as e:
            logger.error(f"Error adding background music: {e}")
            raise

    async def normalize_audio(
        self, audio_data: bytes, target_db: float = -16.0, sample_rate: int = 22050
    ) -> bytes:
        """Normalize audio to target dB level"""
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            normalized = self._normalize_audio(audio_segment, target_db)
            output_buffer = io.BytesIO()
            normalized.export(output_buffer, format="mp3", bitrate="192k")
            return output_buffer.getvalue()
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            raise

    async def get_audio_info(self, audio_data: bytes) -> dict:
        """Get audio information"""
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            return {
                "duration_ms": len(audio_segment),
                "duration_seconds": len(audio_segment) / 1000.0,
                "channels": audio_segment.channels,
                "sample_rate": audio_segment.frame_rate,
                "bit_depth": audio_segment.sample_width * 8,
                "size_bytes": len(audio_data),
                "dBFS": audio_segment.dBFS,
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            raise

    async def get_audio_info_from_file(self, file_path: str) -> dict:
        """Get audio information from file"""
        try:
            audio_segment = AudioSegment.from_file(file_path)
            file_size = Path(file_path).stat().st_size
            return {
                "duration_ms": len(audio_segment),
                "duration_seconds": len(audio_segment) / 1000.0,
                "channels": audio_segment.channels,
                "sample_rate": audio_segment.frame_rate,
                "bit_depth": audio_segment.sample_width * 8,
                "size_bytes": file_size,
                "dBFS": audio_segment.dBFS,
            }
        except Exception as e:
            logger.error(f"Error getting audio info from file: {e}")
            raise
