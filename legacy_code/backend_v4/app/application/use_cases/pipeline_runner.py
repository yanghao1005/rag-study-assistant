from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from app.core.artifacts import write_json_artifact
from app.domain.models.contracts import PipelineRunResponse
from app.domain.ports.providers import EmbeddingsProvider
from app.domain.ports.repositories import VectorRepository
from app.infrastructure.parsing.pdf_parser import PDFParser
from app.infrastructure.providers.embeddings_provider import EmbeddingsProvider as StubEmbeddingsProvider
from app.infrastructure.repositories.vector_repository import InMemoryVectorRepository


class PipelineRunner:
    """Coordinates stage-based ingestion/retrieval pipeline execution."""

    STAGES: tuple[str, ...] = (
        "validate_input",
        "parse_document",
        "detect_sections",
        "semantic_chunking",
        "build_embeddings",
        "persist_vectors",
        "build_summary_index",
        "extract_graph_triplets",
    )

    def __init__(
        self,
        *,
        vector_repository: VectorRepository | None = None,
        embeddings_provider: EmbeddingsProvider | None = None,
        pdf_parser: PDFParser | None = None,
        artifacts_dir: str = "debug_artifacts",
    ) -> None:
        self._vector_repository = vector_repository or InMemoryVectorRepository()
        self._embeddings_provider = embeddings_provider or StubEmbeddingsProvider()
        self._pdf_parser = pdf_parser or PDFParser()
        self._artifacts_dir = artifacts_dir

    def run(self, payload: dict) -> dict:
        document_id = payload.get("document_id")
        if not document_id:
            raise ValueError("document_id is required")
        if not payload.get("file_path"):
            raise ValueError("file_path is required")

        run_id = str(uuid4())

        executed_stages = self._select_stages(
            stage=payload.get("stage"),
            from_stage=payload.get("from") or payload.get("from_stage"),
            to_stage=payload.get("to") or payload.get("to_stage"),
        )

        stage_results: list[dict] = []
        context: dict = {"document_id": document_id, "checks_passed": True, "payload": payload}

        for stage_name in executed_stages:
            start = perf_counter()
            stage_output = self._run_stage(stage_name=stage_name, context=context)
            check_result = self._check_stage(stage_name=stage_name, stage_output=stage_output)
            stage_status = "ok" if check_result["passed"] else "error"
            duration_ms = int((perf_counter() - start) * 1000)

            artifact_path = write_json_artifact(
                root_dir=self._artifacts_dir,
                run_id=run_id,
                name=stage_name,
                payload={
                    "document_id": document_id,
                    "run_id": run_id,
                    "stage": stage_name,
                    "duration_ms": duration_ms,
                    "output": stage_output,
                    "check": check_result,
                },
            )

            stage_results.append(
                {
                    "stage": stage_name,
                    "status": stage_status,
                    "duration_ms": duration_ms,
                    "details": {
                        "artifact": artifact_path,
                        "checks": [check_result],
                    },
                }
            )

            context[stage_name] = stage_output
            if not check_result["passed"]:
                context["checks_passed"] = False
                break

        output = {
            "indexed": any(stage_name in {"persist_vectors", "build_summary_index"} for stage_name in executed_stages),
            "last_stage": executed_stages[-1] if executed_stages else None,
            "checks_passed": context["checks_passed"],
            "run_id": run_id,
        }

        response = PipelineRunResponse(
            request_id=None,
            document_id=document_id,
            executed_stages=executed_stages,
            stage_results=stage_results,
            output=output,
        )
        return response.model_dump()

    def _select_stages(self, *, stage: str | None, from_stage: str | None, to_stage: str | None) -> list[str]:
        if stage and (from_stage or to_stage):
            raise ValueError("Use either stage or from/to range, not both")

        if stage:
            return [self._validate_stage(stage)]

        if from_stage or to_stage:
            if not (from_stage and to_stage):
                raise ValueError("Both from and to must be provided")
            start = self._stage_index(from_stage)
            end = self._stage_index(to_stage)
            if start > end:
                raise ValueError("from stage must come before to stage")
            return list(self.STAGES[start : end + 1])

        return list(self.STAGES)

    def _stage_index(self, stage_name: str) -> int:
        validated = self._validate_stage(stage_name)
        return self.STAGES.index(validated)

    def _validate_stage(self, stage_name: str) -> str:
        if stage_name not in self.STAGES:
            raise ValueError(f"Unknown stage: {stage_name}")
        return stage_name

    def _run_stage(self, *, stage_name: str, context: dict) -> dict:
        document_id = context["document_id"]
        payload = context.get("payload", {})

        if stage_name == "validate_input":
            return {
                "document_id": document_id,
                "valid": bool(document_id),
                "has_file": bool(payload.get("file_path")),
            }

        if stage_name == "parse_document":
            file_path = payload.get("file_path")
            pages = self._pdf_parser.parse(str(file_path))
            return {"pages": pages}

        if stage_name == "detect_sections":
            pages = context.get("parse_document", {}).get("pages", [])
            if not pages:
                return {"sections": []}
            return {
                "sections": [
                    {
                        "name": "introduction",
                        "page": 1,
                        "preview": str(pages[0])[:120],
                    }
                ]
            }

        if stage_name == "semantic_chunking":
            sections = context.get("detect_sections", {}).get("sections", [])
            chunks = [
                {
                    "id": f"{document_id}-chunk-{index + 1}",
                    "content": section.get("preview", "chunk text"),
                    "page": section.get("page"),
                    "chapter_name": section.get("name"),
                    "document_type": "pdf",
                }
                for index, section in enumerate(sections)
            ]
            return {"chunks": chunks}

        if stage_name == "build_embeddings":
            chunks = context.get("semantic_chunking", {}).get("chunks", [])
            for chunk in chunks:
                chunk["embedding"] = self._embeddings_provider.embed(str(chunk.get("content", "")))
                chunk["score"] = 0.8
            return {"embeddings_count": len(chunks), "chunks": chunks}

        if stage_name == "persist_vectors":
            chunks = context.get("build_embeddings", {}).get("chunks", [])
            user_id = str(payload.get("user_id") or "00000000-0000-0000-0000-000000000000")
            persisted = self._vector_repository.save_chunks(
                document_id=document_id,
                chunks=chunks,
                scope="document",
                scope_id=document_id,
                user_id=user_id,
            )
            return {"persisted": persisted > 0, "persisted_chunks": persisted}

        if stage_name == "build_summary_index":
            chunks = context.get("build_embeddings", {}).get("chunks", [])
            return {
                "summary_nodes": 1 if chunks else 0,
                "summary": str(chunks[0].get("content", ""))[:200] if chunks else "",
            }

        if stage_name == "extract_graph_triplets":
            chunks = context.get("build_embeddings", {}).get("chunks", [])
            return {"triplets": 1 if chunks else 0}

        return {}

    def _check_stage(self, *, stage_name: str, stage_output: dict) -> dict:
        checks = {
            "validate_input": lambda output: output.get("valid", False),
            "parse_document": lambda output: len(output.get("pages", [])) > 0,
            "detect_sections": lambda output: len(output.get("sections", [])) > 0,
            "semantic_chunking": lambda output: len(output.get("chunks", [])) > 0,
            "build_embeddings": lambda output: int(output.get("embeddings_count", 0)) > 0,
            "persist_vectors": lambda output: bool(output.get("persisted", False)) and int(output.get("persisted_chunks", 0)) > 0,
            "build_summary_index": lambda output: int(output.get("summary_nodes", 0)) > 0,
            "extract_graph_triplets": lambda output: int(output.get("triplets", 0)) > 0,
        }
        check_fn = checks.get(stage_name, lambda _: True)
        passed = bool(check_fn(stage_output))
        return {
            "name": f"{stage_name}_check",
            "passed": passed,
            "message": "ok" if passed else "check failed",
        }
