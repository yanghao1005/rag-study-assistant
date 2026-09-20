from dataclasses import dataclass


@dataclass(frozen=True)
class ChatContext:
    user_id: str
    scope: str
    scope_id: str
    question: str
