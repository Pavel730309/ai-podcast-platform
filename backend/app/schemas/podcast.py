"""
Pydantic schemas for API validation and serialization
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PodcastStyleEnum(str, Enum):
    ACADEMIC = "academic"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"


class PodcastStatusEnum(str, Enum):
    PENDING = "pending"
    EXTRACTING_TEXT = "extracting_text"
    GENERATING_SCENARIO = "generating_scenario"
    SYNTHESIZING_SPEECH = "synthesizing_speech"
    PROCESSING_AUDIO = "processing_audio"
    GENERATING_COVER = "generating_cover"
    COMPLETED = "completed"
    FAILED = "failed"


class SourceTypeEnum(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    URL = "url"
    TEXT = "text"


# User schemas
class UserBase(BaseModel):
    email: str = Field(..., email=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Voice schemas
class VoiceSettings(BaseModel):
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: Optional[float] = Field(1.0, ge=0.5, le=2.0)


class ParticipantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., pattern="^(host|expert|commentator)$")
    voice_provider: str = Field(..., pattern="^(openai|elevenlabs|google)$")
    voice_id: str
    voice_settings: Optional[VoiceSettings] = None


class ParticipantResponse(ParticipantCreate):
    id: str
    
    class Config:
        from_attributes = True


# Podcast schemas
class PodcastBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    style: PodcastStyleEnum = PodcastStyleEnum.ENTERTAINMENT
    num_participants: int = Field(2, ge=2, le=4)


class PodcastCreate(PodcastBase):
    source_type: SourceTypeEnum
    source_url: Optional[str] = None
    source_text: Optional[str] = None
    participants: List[ParticipantCreate]


class PodcastUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    style: Optional[PodcastStyleEnum] = None


class PodcastResponse(PodcastBase):
    id: str
    user_id: str
    status: PodcastStatusEnum
    source_type: str
    source_file: Optional[str]
    source_url: Optional[str]
    audio_file: Optional[str]
    cover_image: Optional[str]
    rss_feed: Optional[str]
    duration_seconds: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PodcastDetailResponse(PodcastResponse):
    extracted_text: Optional[str]
    scenario: Optional[str]
    participants: List[ParticipantResponse]


# Text extraction schemas
class TextExtractionRequest(BaseModel):
    source_type: SourceTypeEnum
    url: Optional[str] = None
    text: Optional[str] = None


class TextExtractionResponse(BaseModel):
    text: str
    title: Optional[str]
    author: Optional[str]
    source_type: str
    word_count: int
    character_count: int
    estimated_reading_time: int


# Scenario generation schemas
class ScenarioGenerateRequest(BaseModel):
    text: str = Field(..., min_length=100)
    style: PodcastStyleEnum = PodcastStyleEnum.ENTERTAINMENT
    num_participants: int = Field(2, ge=2, le=4)
    participant_roles: Optional[List[str]] = None


class DialogueLine(BaseModel):
    participant: str
    role: str
    text: str


class ScenarioGenerateResponse(BaseModel):
    title: str
    description: str
    dialogue: List[DialogueLine]
    total_lines: int
    estimated_duration_minutes: int


# TTS schemas
class TTSRequest(BaseModel):
    text: str = Field(..., max_length=5000)
    provider: str = Field("openai", pattern="^(openai|elevenlabs|google)$")
    voice_id: str
    speed: float = Field(1.0, ge=0.5, le=2.0)


class TTSResponse(BaseModel):
    audio_url: str
    duration_seconds: float
    provider: str
    voice_id: str


# Voice catalog schemas
class VoiceProfileResponse(BaseModel):
    id: str
    provider: str
    voice_id: str
    name: str
    gender: str
    language: str
    description: Optional[str]
    preview_url: Optional[str]
    
    class Config:
        from_attributes = True


# Progress tracking
class ProgressResponse(BaseModel):
    podcast_id: str
    status: PodcastStatusEnum
    progress_percent: int
    current_step: str
    error_message: Optional[str]
    estimated_time_remaining_seconds: Optional[int]


# File upload response
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_size: int
    upload_url: Optional[str] = None


# API Key schemas
class APIKeyCreate(BaseModel):
    provider: str = Field(..., pattern="^(openai|elevenlabs|google)$")
    api_key: str


class APIKeyResponse(APIKeyCreate):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# RSS Feed schemas
class RSSFeedResponse(BaseModel):
    feed_url: str
    podcast_id: str
    title: str
    description: str
    episode_count: int
    last_updated: datetime
