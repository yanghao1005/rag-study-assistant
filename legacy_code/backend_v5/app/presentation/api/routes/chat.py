from fastapi import APIRouter, Depends

from app.container import get_chat_use_case
from app.core.auth import AuthUser
from app.presentation.api.deps.auth import get_current_user
from app.presentation.api.schemas.chat import ChatAskRequest, ChatAskResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatAskResponse)
def ask_chat(
    request: ChatAskRequest,
    user: AuthUser = Depends(get_current_user),
) -> ChatAskResponse:
    return get_chat_use_case().answer(user_id=user.user_id, request=request)
