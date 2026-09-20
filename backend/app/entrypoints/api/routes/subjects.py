"""Subject management routes."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

from app.core.errors import AppError
from app.domain.entities.subject import Subject
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import SubjectCreateRequest, SubjectUpdateRequest

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("")
async def list_subjects(user: CurrentUserDep, container: ContainerDep) -> dict[str, object]:
    items = await container.subjects.list_for_user(user.id)
    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "color": s.color,
                "sort_order": s.sort_order,
            }
            for s in items
        ]
    }


@router.post("", status_code=201)
async def create_subject(
    body: SubjectCreateRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    subject = await container.subjects.create(
        Subject(
            id=str(uuid4()),
            user_id=user.id,
            name=body.name.strip(),
            description=body.description,
            color=body.color,
        )
    )
    return {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "color": subject.color,
        "sort_order": subject.sort_order,
    }


@router.get("/{subject_id}")
async def get_subject(
    subject_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    subject = await container.subjects.get(user_id=user.id, subject_id=subject_id)
    if subject is None:
        raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")
    return {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "color": subject.color,
        "sort_order": subject.sort_order,
    }


@router.patch("/{subject_id}")
async def update_subject(
    subject_id: str,
    body: SubjectUpdateRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    subject = await container.subjects.get(user_id=user.id, subject_id=subject_id)
    if subject is None:
        raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")
    if body.name is not None:
        subject.rename(body.name)
    if body.description is not None:
        subject.description = body.description
    if body.color is not None:
        subject.color = body.color
    if body.sort_order is not None:
        subject.sort_order = body.sort_order
    updated = await container.subjects.update(subject)
    return {
        "id": updated.id,
        "name": updated.name,
        "description": updated.description,
        "color": updated.color,
        "sort_order": updated.sort_order,
    }


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    deleted = await container.subjects.delete(user_id=user.id, subject_id=subject_id)
    if not deleted:
        raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")
    return {"deleted": True}
