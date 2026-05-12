from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, Field


class PipelineRunRequest(BaseModel):
    document_id: str
    file_path: str
    subject_id: str | None = None
    user_id: str | None = None
    stage: str | None = None
    from_stage: str | None = Field(default=None, validation_alias=AliasChoices("from_stage", "from"))
    to_stage: str | None = Field(default=None, validation_alias=AliasChoices("to_stage", "to"))
    debug: bool = False

    def to_payload(self) -> dict[str, Any]:
        data = self.model_dump()
        if data.get("from_stage") and not data.get("from"):
            data["from"] = data["from_stage"]
        if data.get("to_stage") and not data.get("to"):
            data["to"] = data["to_stage"]
        return data
