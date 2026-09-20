from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationContext:
    user_id: str
    scope: str
    scope_id: str
    query: str
