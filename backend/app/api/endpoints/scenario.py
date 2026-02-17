"""
API endpoints for scenario generation
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List

from app.schemas import (
    ScenarioGenerateRequest,
    ScenarioGenerateResponse,
    DialogueLine
)
from app.services.scenario import ScenarioService

router = APIRouter(prefix="/scenario", tags=["scenario"])

# Initialize service
scenario_service = ScenarioService()


@router.post("/generate", response_model=ScenarioGenerateResponse)
async def generate_scenario(request: ScenarioGenerateRequest):
    """
    Generate a podcast scenario from text
    
    - **text**: Source text to convert to dialogue (minimum 100 characters)
    - **style**: Podcast style (academic, entertainment, business)
    - **num_participants**: Number of participants (2-4)
    - **participant_roles**: Optional list of roles for each participant
    """
    result = await scenario_service.generate_scenario(
        text=request.text,
        style=request.style.value,
        num_participants=request.num_participants,
        participant_roles=request.participant_roles
    )
    
    if result.error:
        raise HTTPException(status_code=400, detail=result.error)
    
    return ScenarioGenerateResponse(
        title=result.title,
        description=result.description,
        dialogue=[
            DialogueLine(
                participant=line.participant,
                role=line.role,
                text=line.text
            )
            for line in result.dialogue
        ],
        total_lines=result.total_lines,
        estimated_duration_minutes=result.estimated_duration_minutes
    )


@router.get("/providers")
async def get_available_providers():
    """Get list of available AI providers"""
    return {
        "providers": scenario_service.get_available_providers()
    }
