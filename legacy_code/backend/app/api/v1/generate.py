"""
Generation API endpoints
"""
from typing import List, Literal, Optional
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field

from app.services.content_generator import ContentGenerator
from app.core.logging import logger

router = APIRouter(prefix="/generate", tags=["generation"])
generator = ContentGenerator()

class GenerateRequest(BaseModel):
    scope: Literal["subject", "document", "chapter"]
    scope_id: str
    topic: Optional[str] = None
    count: int = Field(default=5, ge=1, le=20)
    difficulty: Optional[Literal["easy", "medium", "hard"]] = "medium"

@router.post("/flashcards")
async def generate_flashcards(request: GenerateRequest):
    """Generate flashcards from context"""
    try:
        result = await generator.generate_flashcards(
            scope=request.scope,
            scope_id=request.scope_id,
            topic=request.topic,
            count=request.count
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate flashcards"
        )

@router.post("/quiz")
async def generate_quiz(request: GenerateRequest):
    """Generate quiz from context"""
    try:
        result = await generator.generate_quiz(
            scope=request.scope,
            scope_id=request.scope_id,
            topic=request.topic,
            count=request.count,
            difficulty=request.difficulty
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating quiz: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz"
        )
