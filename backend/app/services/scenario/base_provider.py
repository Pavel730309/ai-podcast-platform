"""
Base AI provider interface for scenario generation
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class PodcastStyle(str, Enum):
    ACADEMIC = "academic"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"


@dataclass
class DialogueLine:
    """Single line of dialogue"""
    participant: str
    role: str
    text: str


@dataclass
class ScenarioResult:
    """Result of scenario generation"""
    title: str
    description: str
    dialogue: List[DialogueLine]
    total_lines: int
    estimated_duration_minutes: int
    error: Optional[str] = None


@dataclass
class Participant:
    """Podcast participant"""
    name: str
    role: str  # host, expert, commentator
    personality: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_scenario(
        self,
        text: str,
        style: PodcastStyle,
        participants: List[Participant],
        title: Optional[str] = None
    ) -> ScenarioResult:
        """
        Generate podcast scenario from text
        
        Args:
            text: Source text to convert to dialogue
            style: Podcast style
            participants: List of participants
            title: Optional title for the podcast
            
        Returns:
            ScenarioResult with generated dialogue
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the AI provider is available"""
        pass
