"""
Scenario generation service
"""
from typing import Optional, List
import json

from app.services.scenario.base_provider import (
    BaseAIProvider,
    PodcastStyle,
    Participant,
    ScenarioResult,
    DialogueLine
)
from app.services.scenario.openai_provider import OpenAIProvider


class ScenarioService:
    """Service for generating podcast scenarios"""
    
    def __init__(self):
        self.providers: dict[str, BaseAIProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers"""
        # Register OpenAI provider
        openai_provider = OpenAIProvider()
        self.providers["openai"] = openai_provider
    
    def register_provider(self, name: str, provider: BaseAIProvider):
        """Register a new AI provider"""
        self.providers[name] = provider
    
    async def generate_scenario(
        self,
        text: str,
        style: str = "entertainment",
        num_participants: int = 2,
        participant_roles: Optional[List[str]] = None,
        provider: str = "openai",
        title: Optional[str] = None
    ) -> ScenarioResult:
        """
        Generate a podcast scenario from text
        
        Args:
            text: Source text to convert to dialogue
            style: Podcast style (academic, entertainment, business)
            num_participants: Number of participants (2-4)
            participant_roles: Optional list of roles for each participant
            provider: AI provider to use
            title: Optional title for the podcast
            
        Returns:
            ScenarioResult with generated dialogue
        """
        # Validate inputs
        if not text or len(text.strip()) < 100:
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error="Text is too short for scenario generation (minimum 100 characters)"
            )
        
        # Get provider
        ai_provider = self.providers.get(provider)
        if not ai_provider:
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error=f"AI provider '{provider}' not found"
            )
        
        # Check if provider is available
        if not await ai_provider.is_available():
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error=f"AI provider '{provider}' is not available (check API key)"
            )
        
        # Parse style
        try:
            podcast_style = PodcastStyle(style.lower())
        except ValueError:
            podcast_style = PodcastStyle.ENTERTAINMENT
        
        # Create participants
        participants = self._create_participants(num_participants, participant_roles)
        
        # Generate scenario
        result = await ai_provider.generate_scenario(
            text=text,
            style=podcast_style,
            participants=participants,
            title=title
        )
        
        return result
    
    def _create_participants(
        self,
        num_participants: int,
        roles: Optional[List[str]] = None
    ) -> List[Participant]:
        """Create participant profiles"""
        default_names = ["Alex", "Jordan", "Sam", "Taylor"]
        default_roles = ["host", "expert", "commentator", "guest"]
        default_personalities = [
            "Enthusiastic and curious, asks great questions",
            "Knowledgeable and articulate, provides detailed explanations",
            "Analytical and thoughtful, offers different perspectives",
            "Friendly and relatable, connects with the audience"
        ]
        
        participants = []
        
        for i in range(min(num_participants, 4)):
            role = roles[i] if roles and i < len(roles) else default_roles[i]
            participants.append(Participant(
                name=default_names[i],
                role=role,
                personality=default_personalities[i]
            ))
        
        return participants
    
    def scenario_to_json(self, result: ScenarioResult) -> str:
        """Convert scenario result to JSON string"""
        data = {
            "title": result.title,
            "description": result.description,
            "dialogue": [
                {
                    "participant": line.participant,
                    "role": line.role,
                    "text": line.text
                }
                for line in result.dialogue
            ],
            "total_lines": result.total_lines,
            "estimated_duration_minutes": result.estimated_duration_minutes
        }
        
        if result.error:
            data["error"] = result.error
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def json_to_scenario(self, json_str: str) -> ScenarioResult:
        """Parse JSON string to ScenarioResult"""
        try:
            data = json.loads(json_str)
            return ScenarioResult(
                title=data.get("title", ""),
                description=data.get("description", ""),
                dialogue=[
                    DialogueLine(
                        participant=line["participant"],
                        role=line["role"],
                        text=line["text"]
                    )
                    for line in data.get("dialogue", [])
                ],
                total_lines=data.get("total_lines", 0),
                estimated_duration_minutes=data.get("estimated_duration_minutes", 0),
                error=data.get("error")
            )
        except (json.JSONDecodeError, KeyError) as e:
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error=f"Failed to parse scenario JSON: {str(e)}"
            )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return list(self.providers.keys())
