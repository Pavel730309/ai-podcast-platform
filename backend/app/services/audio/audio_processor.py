"""
Audio processing service for podcast creation
"""

import io
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from pydub import AudioSegment

from app.config import settings


class AudioProcessor:
    """Service for audio processing operations"""

    def __init__(self):
        self.supported_formats = ["mp3", "wav", "flac"]

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
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{output_format}"
                )
                temp_file.write(segment_data)
                temp_file.flush()
                temp_file.close()
                temp_files.append(temp_file.name)

                # Load audio segment
                audio_segment = AudioSegment.from_file(temp_file.name)

                # If this is the first segment, initialize combined audio
                if combined_audio is None:
                    combined_audio = audio_segment
                else:
                    # Add silence between segments (100ms)
                    silence = AudioSegment.silent(duration=100)
                    combined_audio += silence + audio_segment

            # Export combined audio
            if combined_audio:
                output_buffer = io.BytesIO()
                combined_audio.export(output_buffer, format=output_format)
                output_data = output_buffer.getvalue()

                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass

                return output_data
            else:
                # Return empty bytes if no segments
                return b""

        except Exception as e:
            # Clean up temporary files on error
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
            raise Exception(f"Error combining audio segments: {str(e)}")

    async def add_background_music(
        self,
        speech_audio: bytes,
        music_audio: bytes,
        music_volume_ratio: float = 0.3,
        fade_duration: int = 2000,
    ) -> bytes:
        """
        Add background music to speech audio

        Args:
            speech_audio: Speech audio bytes
            music_audio: Background music audio bytes
            music_volume_ratio: Volume ratio for music (0.0 to 1.0)
            fade_duration: Fade duration in milliseconds

        Returns:
            Audio with background music as bytes
        """
        try:
            # Load both audio files
            speech_segment = AudioSegment.from_file(io.BytesIO(speech_audio))
            music_segment = AudioSegment.from_file(io.BytesIO(music_audio))

            # Adjust music volume
            music_segment = music_segment - (20 * (1 - music_volume_ratio))

            # Make music loop if shorter than speech
            if len(music_segment) < len(speech_segment):
                # Repeat music to match speech length
                repeats = len(speech_segment) // len(music_segment) + 1
                music_segment = music_segment * repeats

            # Trim music to match speech length
            music_segment = music_segment[: len(speech_segment)]

            # Apply fade in/out to music
            music_segment = music_segment.fade_in(fade_duration).fade_out(fade_duration)

            # Mix audio
            mixed_audio = speech_segment.overlay(music_segment)

            # Export result
            output_buffer = io.BytesIO()
            mixed_audio.export(output_buffer, format="mp3")
            return output_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error adding background music: {str(e)}")

    async def normalize_audio(
        self, audio_data: bytes, target_db: float = -20.0, sample_rate: int = 22050
    ) -> bytes:
        """
        Normalize audio to target dB level

        Args:
            audio_data: Audio data as bytes
            target_db: Target dB level
            sample_rate: Sample rate

        Returns:
            Normalized audio as bytes
        """
        try:
            # Load audio
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))

            # Normalize
            change_in_db = target_db - audio_segment.dBFS
            normalized_audio = audio_segment.apply_gain(change_in_db)

            # Export
            output_buffer = io.BytesIO()
            normalized_audio.export(output_buffer, format="mp3")
            return output_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error normalizing audio: {str(e)}")

    async def adjust_volume(self, audio_data: bytes, volume_change_db: float) -> bytes:
        """
        Adjust audio volume

        Args:
            audio_data: Audio data as bytes
            volume_change_db: Volume change in dB

        Returns:
            Adjusted audio as bytes
        """
        try:
            # Load audio
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))

            # Apply volume change
            adjusted_audio = audio_segment.apply_gain(volume_change_db)

            # Export
            output_buffer = io.BytesIO()
            adjusted_audio.export(output_buffer, format="mp3")
            return output_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error adjusting audio volume: {str(e)}")

    async def add_silence(self, audio_data: bytes, duration_ms: int = 1000) -> bytes:
        """
        Add silence to beginning or end of audio

        Args:
            audio_data: Audio data as bytes
            duration_ms: Duration of silence in milliseconds

        Returns:
            Audio with added silence as bytes
        """
        try:
            # Load audio
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))

            # Add silence
            silence = AudioSegment.silent(duration=duration_ms)
            audio_with_silence = silence + audio_segment

            # Export
            output_buffer = io.BytesIO()
            audio_with_silence.export(output_buffer, format="mp3")
            return output_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error adding silence: {str(e)}")

    async def get_audio_info(self, audio_data: bytes) -> dict:
        """
        Get audio information

        Args:
            audio_data: Audio data as bytes

        Returns:
            Dictionary with audio information
        """
        try:
            # Load audio
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))

            return {
                "duration_ms": len(audio_segment),
                "channels": audio_segment.channels,
                "sample_rate": audio_segment.frame_rate,
                "bit_depth": audio_segment.sample_width * 8,
                "size_bytes": len(audio_data),
            }
        except Exception as e:
            raise Exception(f"Error getting audio info: {str(e)}")
