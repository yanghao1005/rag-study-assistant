"""
Subject API endpoints
Handles CRUD operations for subjects
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.core.database import get_db
from app.schemas import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    ErrorResponse
)
from app.core.logging import logger

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=List[SubjectResponse])
async def list_subjects():
    """Get all subjects"""
    try:
        db = get_db()
        result = db.table("subjects").select("*").order("created_at", desc=True).execute()
        
        return result.data
    
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: UUID):
    """Get a specific subject by ID"""
    try:
        db = get_db()
        result = db.table("subjects").select("*").eq("id", str(subject_id)).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject {subject_id} not found"
            )
        
        return result.data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subject {subject_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(subject: SubjectCreate):
    """Create a new subject"""
    try:
        db = get_db()
        
        data = {
            "name": subject.name,
            "description": subject.description
        }
        
        result = db.table("subjects").insert(data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create subject"
            )
        
        logger.info(f"Created subject: {result.data[0]['id']}")
        return result.data[0]
    
    except Exception as e:
        logger.error(f"Error creating subject: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: UUID, subject: SubjectUpdate):
    """Update a subject"""
    try:
        db = get_db()
        
        # Check if subject exists
        existing = db.table("subjects").select("id").eq("id", str(subject_id)).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject {subject_id} not found"
            )
        
        # Build update data (only include fields that are set)
        update_data = {}
        if subject.name is not None:
            update_data["name"] = subject.name
        if subject.description is not None:
            update_data["description"] = subject.description
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        result = db.table("subjects").update(update_data).eq("id", str(subject_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update subject"
            )
        
        logger.info(f"Updated subject: {subject_id}")
        return result.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subject {subject_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: UUID):
    """Delete a subject and all its documents/chunks"""
    try:
        db = get_db()
        
        # Check if subject exists
        existing = db.table("subjects").select("id").eq("id", str(subject_id)).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject {subject_id} not found"
            )
        
        # Delete (cascade will handle documents and chunks)
        db.table("subjects").delete().eq("id", str(subject_id)).execute()
        
        logger.info(f"Deleted subject: {subject_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting subject {subject_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{subject_id}/documents", response_model=List[dict])
async def get_subject_documents(subject_id: UUID):
    """Get all documents for a subject"""
    try:
        db = get_db()
        
        # Check if subject exists
        subject = db.table("subjects").select("id").eq("id", str(subject_id)).execute()
        if not subject.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject {subject_id} not found"
            )
        
        # Get documents
        result = db.table("documents") \
            .select("*") \
            .eq("subject_id", str(subject_id)) \
            .order("created_at", desc=True) \
            .execute()
        
        return result.data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents for subject {subject_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
