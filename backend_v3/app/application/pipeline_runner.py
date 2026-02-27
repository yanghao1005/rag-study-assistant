import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import get_settings
from app.core.dependencies import get_vector_repository
from app.core.exceptions import AppError
from app.domain.pipeline import PIPELINE_ORDER, PipelineRunRequest, PipelineRunResponse, PipelineStage, StageResult
from app.infrastructure.services import (
    build_document_index,
    chunk_document,
    generate_embeddings,
    generate_output,
    parse_document,
    retrieve_context,
)
from app.infrastructure.chapter_detector import detect_chapters
from app.infrastructure.repository import VectorRepository


class PipelineRunner:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.repository: VectorRepository = get_vector_repository()

    def _stages_to_run(self, request: PipelineRunRequest) -> List[PipelineStage]:
        if request.stage:
            return [request.stage]
        if request.from_stage and request.to_stage:
            start_index = PIPELINE_ORDER.index(request.from_stage)
            end_index = PIPELINE_ORDER.index(request.to_stage)
            if start_index > end_index:
                raise AppError("invalid_stage_range", "'from' stage must be before 'to' stage")
            return PIPELINE_ORDER[start_index : end_index + 1]
        return PIPELINE_ORDER

    def _persist_debug_artifact(self, document_id: str, artifact: Dict[str, Any]) -> None:
        debug_dir = Path(self.settings.debug_artifacts_dir)
        debug_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target_file = debug_dir / f"{document_id}_{timestamp}.json"
        target_file.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")

    def run(self, request: PipelineRunRequest, request_id: str | None = None) -> PipelineRunResponse:
        data: Dict[str, Any] = {
            "document_id": request.document_id,
            "user_id": request.user_id,
            "subject_id": request.subject_id,
            "query": request.query or "summarize the document",
            "document_text": request.document_text or "",
            "file_path": request.file_path,
            "document_type": request.document_type,
        }
        stage_results: List[StageResult] = []
        executed_stages = self._stages_to_run(request)

        for stage in executed_stages:
            if stage == PipelineStage.VALIDATE_INPUT:
                if not data["document_id"]:
                    raise AppError("validation_error", "document_id is required")
                if stage in executed_stages and PipelineStage.STORE_VECTORS in executed_stages and not data.get("user_id"):
                    raise AppError("validation_error", "user_id is required when storing vectors")
                if data["document_type"] == "pdf" and not data.get("file_path") and not data.get("document_text"):
                    raise AppError("validation_error", "file_path or document_text is required for pdf document")
                if data["document_type"] == "summary" and not data.get("document_text"):
                    raise AppError("validation_error", "document_text is required for summary document")
                if not data["document_text"] and data["document_type"] == "pdf":
                    stage_results.append(StageResult(stage=stage, details={"warning": "using file_path parsing for pdf"}))
                    continue
                stage_results.append(StageResult(stage=stage, details={"ok": True}))

            elif stage == PipelineStage.PARSE_DOCUMENT:
                parsed = parse_document(
                    document_type=data["document_type"],
                    document_text=data.get("document_text"),
                    file_path=data.get("file_path"),
                )
                data.update(parsed)
                stage_results.append(StageResult(stage=stage, details={"total_pages": parsed["total_pages"]}))

            elif stage == PipelineStage.DETECT_CHAPTERS:
                pages = data.get("pages", [])
                chapters = detect_chapters(pages)
                data["chapters"] = chapters
                stage_results.append(StageResult(stage=stage, details={"chapter_count": len(chapters)}))

            elif stage == PipelineStage.SPLIT_CHUNKS:
                pages = data.get("pages", [])
                chunks = chunk_document(
                    pages=pages,
                    chunk_size=self.settings.chunk_size,
                    chunk_overlap=self.settings.chunk_overlap,
                    subject_id=data.get("subject_id"),
                    document_type=data.get("document_type", "summary"),
                    chapters=data.get("chapters", []),
                )
                data["chunks"] = chunks
                stage_results.append(StageResult(stage=stage, details={"chunk_count": len(chunks)}))

            elif stage == PipelineStage.GENERATE_EMBEDDINGS:
                chunks = data.get("chunks", [])
                embeddings = generate_embeddings(
                    chunks,
                    model=self.settings.embedding_model,
                    api_key=self.settings.openai_api_key or None,
                )
                data["embeddings"] = embeddings
                stage_results.append(StageResult(stage=stage, details={"embedding_count": len(embeddings)}))

            elif stage == PipelineStage.STORE_VECTORS:
                stored_count = self.repository.store_chunks(
                    document_id=data["document_id"],
                    user_id=data.get("user_id"),
                    chunks=data.get("chunks", []),
                    embeddings=data.get("embeddings", []),
                )
                data["stored_count"] = stored_count
                stage_results.append(StageResult(stage=stage, details={"stored_count": stored_count}))

            elif stage == PipelineStage.BUILD_DOCUMENT_INDEX:
                index_payload = build_document_index(data.get("chunks", []))
                data["document_index"] = index_payload
                self.repository.persist_document_index(
                    document_id=data["document_id"],
                    user_id=data.get("user_id"),
                    index_payload=index_payload,
                )
                stage_results.append(StageResult(stage=stage, details=index_payload))

            elif stage == PipelineStage.RETRIEVE_CONTEXT:
                rows = self.repository.retrieve(
                    query=data["query"],
                    top_k=self.settings.top_k,
                    scope="subject" if data.get("subject_id") else None,
                    scope_id=data.get("subject_id"),
                )
                context = retrieve_context(rows)
                data["context_chunks"] = context
                stage_results.append(StageResult(stage=stage, details={"retrieved": len(context)}))

            elif stage == PipelineStage.GENERATE_OUTPUT:
                output = generate_output(data["query"], data.get("context_chunks", []))
                data["output"] = output
                stage_results.append(StageResult(stage=stage, details={"source_count": len(output.get("sources", []))}))

        if request.debug:
            self._persist_debug_artifact(
                document_id=request.document_id,
                artifact={
                    "request_id": request_id,
                    "document_id": request.document_id,
                    "executed_stages": [stage.value for stage in executed_stages],
                    "stage_results": [result.model_dump() for result in stage_results],
                    "output": data.get("output", {}),
                },
            )

        return PipelineRunResponse(
            request_id=request_id,
            document_id=request.document_id,
            executed_stages=executed_stages,
            stage_results=stage_results,
            output=data.get("output", {}),
        )
