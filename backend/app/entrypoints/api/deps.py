"""FastAPI dependency injection helpers."""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, Header, Request

from app.container import AppContainer
from app.core.errors import AppError
from app.ports.auth import AuthenticatedUser


def get_container(request: Request) -> AppContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise AppError(
            status_code=500,
            error="container_missing",
            message="Application container is not initialized.",
        )
    return cast(AppContainer, container)


ContainerDep = Annotated[AppContainer, Depends(get_container)]


async def get_current_user(
    container: ContainerDep,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    if not authorization:
        raise AppError(
            status_code=401,
            error="unauthorized",
            message="Missing authorization header.",
        )
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise AppError(
            status_code=401,
            error="unauthorized",
            message="Invalid authorization header.",
        )
    token = authorization[len(prefix) :].strip()
    if not token:
        raise AppError(status_code=401, error="unauthorized", message="Empty bearer token.")
    return await container.auth.verify_token(token)


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]
