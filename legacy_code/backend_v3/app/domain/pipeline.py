from enum import Enum
from typing import Literal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelineStage(str, Enum):
    VALIDATE_INPUT = "validate_input"
    PARSE_DOCUMENT = "parse_document"
    DETECT_CHAPTERS = "detect_chapters"
    SPLIT_CHUNKS = "split_chunks"
    GENERATE_EMBEDDINGS = "generate_embeddings"
    STORE_VECTORS = "store_vectors"
    BUILD_DOCUMENT_INDEX = "build_document_index"
    RETRIEVE_CONTEXT = "retrieve_context"
    GENERATE_OUTPUT = "generate_output"


PIPELINE_ORDER: List[PipelineStage] = [
    PipelineStage.VALIDATE_INPUT,
    PipelineStage.PARSE_DOCUMENT,
    PipelineStage.DETECT_CHAPTERS,
    PipelineStage.SPLIT_CHUNKS,
    PipelineStage.GENERATE_EMBEDDINGS,
    PipelineStage.STORE_VECTORS,
    PipelineStage.BUILD_DOCUMENT_INDEX,
    PipelineStage.RETRIEVE_CONTEXT,
    PipelineStage.GENERATE_OUTPUT,
]


class PipelineRunRequest(BaseModel):
    document_id: str
    user_id: Optional[str] = None
    subject_id: Optional[str] = None
    query: Optional[str] = None
    document_text: Optional[str] = None
    file_path: Optional[str] = None
    document_type: Literal["pdf", "summary"] = "summary"
    stage: Optional[PipelineStage] = None
    from_stage: Optional[PipelineStage] = Field(default=None, alias="from")
    to_stage: Optional[PipelineStage] = Field(default=None, alias="to")
    debug: bool = False


class StageResult(BaseModel):
    stage: PipelineStage
    ok: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class PipelineRunResponse(BaseModel):
    request_id: Optional[str] = None
    document_id: str
    executed_stages: List[PipelineStage]
    stage_results: List[StageResult]
    output: Dict[str, Any] = Field(default_factory=dict)
