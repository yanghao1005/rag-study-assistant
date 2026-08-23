"""Current user profile routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.domain.entities.profile import Profile
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import ProfileUpdateRequest

router = APIRouter(prefix="/me", tags=["profile"])


def _serialize(profile: Profile, *, email: str | None) -> dict[str, object]:
    return {
        "id": profile.id,
        "email": email,
        "display_name": profile.display_name,
        "avatar_url": profile.avatar_url,
        "onboarding_completed": profile.onboarding_completed,
        "preferences": profile.preferences,
    }


@router.get("")
async def get_me(user: CurrentUserDep, container: ContainerDep) -> dict[str, object]:
    profile = await container.profiles.get(user.id)
    if profile is None:
        profile = await container.profiles.upsert(
            Profile(id=user.id, display_name=user.email)
        )
    return _serialize(profile, email=user.email)


@router.patch("")
async def update_me(
    body: ProfileUpdateRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    profile = await container.profiles.get(user.id)
    if profile is None:
        profile = Profile(id=user.id, display_name=user.email)
    if body.display_name is not None:
        profile.display_name = body.display_name.strip() or profile.display_name
    if body.preferences is not None:
        profile.preferences = {**profile.preferences, **body.preferences}
    saved = await container.profiles.upsert(profile)
    return _serialize(saved, email=user.email)
