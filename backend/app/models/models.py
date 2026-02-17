"""
Database models for AI Podcast Platform
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class PodcastStatus(str, enum.Enum):
    """Podcast generation status"""
    PENDING = "pending"
    EXTRACTING_TEXT = "extracting_text"
    GENERATING_SCENARIO = "generating_scenario"
    SYNTHESIZING_SPEECH = "synthesizing_speech"
    PROCESSING_AUDIO = "processing_audio"
    GENERATING_COVER = "generating_cover"
    COMPLETED = "completed"
    FAILED = "failed"


class PodcastStyle(str, enum.Enum):
    """Podcast style options"""
    ACADEMIC = "academic"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    podcasts = relationship("Podcast", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class APIKey(Base):
    """User API keys for external services"""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # openai, elevenlabs, google
    api_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class Podcast(Base):
    """Podcast model"""
    __tablename__ = "podcasts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(PodcastStatus), default=PodcastStatus.PENDING)
    style = Column(Enum(PodcastStyle), default=PodcastStyle.ENTERTAINMENT)
    
    # Source information
    source_type = Column(String, nullable=False)  # pdf, docx, url, text
    source_file = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    
    # Extracted text
    extracted_text = Column(Text, nullable=True)
    
    # Generated scenario
    scenario = Column(Text, nullable=True)
    
    # Audio settings
    num_participants = Column(Integer, default=2)
    voice_settings = Column(Text, nullable=True)  # JSON string with voice assignments
    
    # Output files
    audio_file = Column(String, nullable=True)
    cover_image = Column(String, nullable=True)
    rss_feed = Column(String, nullable=True)
    
    # Metadata
    duration_seconds = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="podcasts")
    participants = relationship("PodcastParticipant", back_populates="podcast")
    episodes = relationship("PodcastEpisode", back_populates="podcast")


class PodcastParticipant(Base):
    """Podcast participant/voice configuration"""
    __tablename__ = "podcast_participants"

    id = Column(String, primary_key=True, default=generate_uuid)
    podcast_id = Column(String, ForeignKey("podcasts.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # host, expert, commentator
    voice_provider = Column(String, nullable=False)  # openai, elevenlabs, google
    voice_id = Column(String, nullable=False)
    voice_settings = Column(Text, nullable=True)  # JSON string with additional settings
    
    # Relationships
    podcast = relationship("Podcast", back_populates="participants")


class PodcastEpisode(Base):
    """Individual episode in a podcast series"""
    __tablename__ = "podcast_episodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    podcast_id = Column(String, ForeignKey("podcasts.id"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Audio file
    audio_file = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    podcast = relationship("Podcast", back_populates="episodes")


class MusicTrack(Base):
    """Background music track"""
    __tablename__ = "music_tracks"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # instrumental, electronic, classical
    mood = Column(String, nullable=False)  # relaxing, energetic, neutral
    file_path = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    license_info = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VoiceProfile(Base):
    """Voice profile for TTS"""
    __tablename__ = "voice_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    provider = Column(String, nullable=False)  # openai, elevenlabs, google
    voice_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)  # male, female, neutral
    language = Column(String, default="en")
    description = Column(Text, nullable=True)
    preview_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
