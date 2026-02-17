"""
OpenAI provider for scenario generation
"""
import json
from typing import Optional, List
import openai

from app.services.scenario.base_provider import (
    BaseAIProvider,
    PodcastStyle,
    Participant,
    ScenarioResult,
    DialogueLine
)
from app.config import settings


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider for scenario generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.client is not None
    
    def _get_system_prompt(self, style: PodcastStyle, participants: List[Participant]) -> str:
        """Generate system prompt based on style and participants"""
        
        participant_descriptions = "\n".join([
            f"- {p.name} ({p.role}): {p.personality or 'A knowledgeable and engaging speaker'}"
            for p in participants
        ])
        
        style_instructions = {
            PodcastStyle.ACADEMIC: """
                The podcast should have an academic tone with:
                - Clear explanations of complex concepts
                - References to research and evidence
                - Thoughtful analysis and critical thinking
                - Professional language while remaining accessible
                - Examples and analogies to clarify difficult points
            """,
            PodcastStyle.ENTERTAINMENT: """
                The podcast should be entertaining with:
                - Engaging and lively conversation
                - Humor and wit where appropriate
                - Interesting anecdotes and stories
                - Accessible language for general audience
                - Dynamic interaction between participants
            """,
            PodcastStyle.BUSINESS: """
                The podcast should have a business focus with:
                - Practical insights and takeaways
                - Industry trends and analysis
                - Professional but conversational tone
                - Actionable advice and recommendations
                - Real-world examples and case studies
            """
        }
        
        return f"""You are an expert podcast scriptwriter. Your task is to transform written content into an engaging podcast dialogue.

PARTICIPANTS:
{participant_descriptions}

STYLE GUIDELINES:
{style_instructions.get(style, style_instructions[PodcastStyle.ENTERTAINMENT])}

REQUIREMENTS:
1. Create natural-sounding dialogue between the participants
2. Each participant should have a distinct voice and perspective based on their role
3. Include smooth transitions between topics
4. Add brief introductions and conclusions
5. Make the conversation feel natural with reactions, questions, and follow-ups
6. Break down complex information into digestible parts
7. Include moments of agreement, elaboration, and occasional friendly debate

OUTPUT FORMAT:
Return a JSON object with the following structure:
{{
    "title": "Podcast episode title",
    "description": "Brief description of the episode",
    "dialogue": [
        {{"participant": "Name", "role": "role", "text": "Dialogue line"}},
        ...
    ]
}}"""
    
    def _get_user_prompt(self, text: str, title: Optional[str] = None) -> str:
        """Generate user prompt with the source text"""
        prompt = "Transform the following text into an engaging podcast dialogue:\n\n"
        if title:
            prompt = f"Title: {title}\n\n"
        prompt += f"SOURCE TEXT:\n{text[:8000]}\n\n"  # Limit text length
        prompt += "Create a podcast dialogue from this content. Make it engaging and natural."
        return prompt
    
    async def generate_scenario(
        self,
        text: str,
        style: PodcastStyle,
        participants: List[Participant],
        title: Optional[str] = None
    ) -> ScenarioResult:
        """Generate podcast scenario using OpenAI"""
        
        if not self.client:
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error="OpenAI API key not configured"
            )
        
        try:
            system_prompt = self._get_system_prompt(style, participants)
            user_prompt = self._get_user_prompt(text, title)
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result_data = json.loads(content)
            
            # Parse dialogue
            dialogue = [
                DialogueLine(
                    participant=line["participant"],
                    role=line["role"],
                    text=line["text"]
                )
                for line in result_data.get("dialogue", [])
            ]
            
            # Calculate estimated duration (average speaking rate: 150 words per minute)
            total_words = sum(len(line.text.split()) for line in dialogue)
            estimated_duration = max(1, round(total_words / 150))
            
            return ScenarioResult(
                title=result_data.get("title", "Untitled Podcast"),
                description=result_data.get("description", ""),
                dialogue=dialogue,
                total_lines=len(dialogue),
                estimated_duration_minutes=estimated_duration
            )
            
        except json.JSONDecodeError as e:
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error=f"Failed to parse AI response: {str(e)}"
            )
        except openai.APIError as e:
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error=f"OpenAI API error: {str(e)}"
            )
        except Exception as e:
            return ScenarioResult(
                title="",
                description="",
                dialogue=[],
                total_lines=0,
                estimated_duration_minutes=0,
                error=f"Unexpected error: {str(e)}"
            )
