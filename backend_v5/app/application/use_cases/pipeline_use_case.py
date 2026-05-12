from __future__ import annotations

import re
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.core.artifacts import write_json_artifact
from app.core.config import get_settings
from app.core.errors import AppError
from app.domain.ports.repositories import StudyRepository
from app.infrastructure.parsing.pdf_parser import PDFParser
from app.infrastructure.parsing.semantic_chunker import SemanticChunker
from openai import OpenAI


class PipelineUseCase:
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

    def __init__(self, *, repository: StudyRepository, pdf_parser: PDFParser, chunker: SemanticChunker) -> None:
        self._repository = repository
        self._pdf_parser = pdf_parser
        self._chunker = chunker
        settings = get_settings()
        self._embeddings_provider = settings.embeddings_provider
        self._embedding_model = settings.openai_embedding_model
        if settings.embeddings_provider == "openai" and settings.openai_api_key:
            self._embedding_client: OpenAI | None = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url or None,
            )
        else:
            self._embedding_client = None

    def run(self, *, user_id: str, payload: dict[str, Any], job_id: str | None = None) -> dict[str, Any]:
        document_id = str(payload.get("document_id") or "").strip()
        file_path = str(payload.get("file_path") or "").strip()
        subject_id = str(payload.get("subject_id") or "").strip()
        if not document_id:
            raise AppError(error="validation_error", message="document_id is required", status_code=400)
        if not file_path:
            raise AppError(error="validation_error", message="file_path is required", status_code=400)

        run_id = str(uuid4())
        debug = bool(payload.get("debug", False))
        selected = self._select_stages(stage=payload.get("stage"), from_stage=payload.get("from"), to_stage=payload.get("to"))

        context: dict[str, Any] = {
            "document_id": document_id,
            "file_path": file_path,
            "subject_id": subject_id,
            "document_type": str(payload.get("document_type") or "pdf"),
            "run_id": run_id,
            "user_id": user_id,
        }
        stage_results: list[dict[str, Any]] = []

        for stage in selected:
            started = perf_counter()
            output = self._run_stage(stage_name=stage, context=context)
            check = self._check_stage(stage_name=stage, output=output)
            duration_ms = int((perf_counter() - started) * 1000)

            details = {"checks": [check]}
            if debug:
                artifact = write_json_artifact(
                    root_dir=get_settings().debug_artifacts_dir,
                    run_id=run_id,
                    name=stage,
                    payload={"stage": stage, "output": output, "check": check, "document_id": document_id},
                )
                details["artifact"] = artifact

            stage_results.append({"stage": stage, "status": "ok" if check["passed"] else "error", "duration_ms": duration_ms, "details": details})
            context[stage] = output

            if job_id:
                self._repository.add_stage_run(job_id=job_id, stage=stage, status="ok" if check["passed"] else "error", duration_ms=duration_ms, details=details)

            if not check["passed"]:
                break

        checks_passed = all(item["status"] == "ok" for item in stage_results)
        return {
            "request_id": None,
            "document_id": document_id,
            "executed_stages": [item["stage"] for item in stage_results],
            "stage_results": stage_results,
            "output": {
                "run_id": run_id,
                "checks_passed": checks_passed,
                "indexed": any(item["stage"] == "persist_vectors" and item["status"] == "ok" for item in stage_results),
                "last_stage": stage_results[-1]["stage"] if stage_results else None,
            },
        }

    def _select_stages(self, *, stage: str | None, from_stage: str | None, to_stage: str | None) -> list[str]:
        if stage and (from_stage or to_stage):
            raise AppError(error="validation_error", message="Use either stage or from/to", status_code=400)
        if stage:
            if stage not in self.STAGES:
                raise AppError(error="validation_error", message=f"Unknown stage: {stage}", status_code=400)
            return [stage]
        if from_stage or to_stage:
            if not from_stage or not to_stage:
                raise AppError(error="validation_error", message="Both from and to are required", status_code=400)
            if from_stage not in self.STAGES or to_stage not in self.STAGES:
                raise AppError(error="validation_error", message="Unknown from/to stage", status_code=400)
            start = self.STAGES.index(from_stage)
            end = self.STAGES.index(to_stage)
            if start > end:
                raise AppError(error="validation_error", message="from must come before to", status_code=400)
            return list(self.STAGES[start : end + 1])
        return list(self.STAGES)

    def _run_stage(self, *, stage_name: str, context: dict[str, Any]) -> dict[str, Any]:
        file_path = context["file_path"]
        document_id = context["document_id"]
        subject_id = context.get("subject_id") or ""
        document_type = str(context.get("document_type") or "pdf")

        if stage_name == "validate_input":
            return {
                "valid": Path(file_path).exists(),
                "document_id": document_id,
                "has_file": Path(file_path).exists(),
            }

        if stage_name == "parse_document":
            pages = self._pdf_parser.parse(file_path)
            return {"pages": pages, "total_pages": len(pages)}

        if stage_name == "detect_sections":
            pages = context.get("parse_document", {}).get("pages", [])
            sections: list[dict[str, Any]] = []
            for page in pages:
                text = str(page.get("text") or "")
                matches = re.findall(r"(?im)^(chapter\s+\d+[^\n]*)", text)
                for name in matches:
                    sections.append({"name": name.strip(), "page": page.get("page")})
            if not sections and pages:
                sections = [{"name": "Section 1", "page": 1}]
            return {"sections": sections}

        if stage_name == "semantic_chunking":
            pages = context.get("parse_document", {}).get("pages", [])
            chunks = self._chunker.chunk(pages=pages)
            for chunk in chunks:
                chunk["document_type"] = document_type
            return {"chunks": chunks}

        if stage_name == "build_embeddings":
            chunks = context.get("semantic_chunking", {}).get("chunks", [])
            if not chunks:
                return {"embeddings_count": 0, "chunks": []}

            texts = [str(chunk.get("content") or "")[:8000] for chunk in chunks]
            vectors = self._build_embeddings(texts)

            embedded_chunks: list[dict[str, Any]] = []
            for chunk, vector in zip(chunks, vectors):
                chunk_copy = dict(chunk)
                chunk_copy["embedding"] = vector
                embedded_chunks.append(chunk_copy)

            return {"embeddings_count": len(embedded_chunks), "chunks": embedded_chunks}

        if stage_name == "persist_vectors":
            chunks = context.get("build_embeddings", {}).get("chunks", [])
            persisted = self._repository.save_chunks(
                user_id=str(context.get("user_id") or ""),
                document_id=document_id,
                subject_id=subject_id,
                chunks=chunks,
            )
            return {"persisted": persisted > 0, "persisted_chunks": persisted}

        if stage_name == "build_summary_index":
            pages = context.get("parse_document", {}).get("pages", [])
            summary_source = "\n".join(str(item.get("text") or "") for item in pages).strip()
            summary = summary_source[:2400]
            self._repository.update_document(
                user_id=str(context.get("user_id") or ""),
                document_id=document_id,
                updates={"content_text": summary, "total_pages": len(pages)},
            )
            return {"summary_nodes": 1 if summary else 0, "summary": summary, "document_type": document_type}

        if stage_name == "extract_graph_triplets":
            chunks = context.get("build_embeddings", {}).get("chunks", []) or context.get("semantic_chunking", {}).get("chunks", [])
            triplets = self._extract_graph_triplets(chunks=chunks, max_triplets=50)
            return {"triplets": len(triplets), "items": triplets}

        raise AppError(error="validation_error", message=f"Unknown stage: {stage_name}", status_code=400)

    def _check_stage(self, *, stage_name: str, output: dict[str, Any]) -> dict[str, Any]:
        checks = {
            "validate_input": bool(output.get("valid")),
            "parse_document": int(output.get("total_pages", 0)) > 0,
            "detect_sections": len(output.get("sections", [])) > 0,
            "semantic_chunking": len(output.get("chunks", [])) > 0,
            "build_embeddings": int(output.get("embeddings_count", 0)) > 0,
            "persist_vectors": bool(output.get("persisted", False)),
            "build_summary_index": int(output.get("summary_nodes", 0)) > 0,
            "extract_graph_triplets": int(output.get("triplets", 0)) >= 0,
        }
        passed = checks.get(stage_name, True)
        return {"name": f"{stage_name}_check", "passed": bool(passed), "message": "ok" if passed else "check failed"}

    def _build_embeddings(self, texts: list[str]) -> list[list[float]]:
        if self._embeddings_provider == "stub":
            return [self._stub_embedding(text) for text in texts]

        if not self._embedding_client:
            raise AppError(
                error="embeddings_not_configured",
                message="OpenAI embeddings provider is required for ingestion embedding stage.",
                status_code=503,
            )

        try:
            response = self._embedding_client.embeddings.create(model=self._embedding_model, input=texts)
        except Exception as exc:
            raise AppError(
                error="embedding_generation_failed",
                message="Embedding generation failed while calling OpenAI.",
                status_code=502,
                details={"type": type(exc).__name__},
            ) from exc

        vectors: list[list[float]] = []
        for item in response.data:
            embedding = getattr(item, "embedding", None)
            if not isinstance(embedding, list) or not embedding:
                raise AppError(
                    error="embedding_output_invalid",
                    message="Embedding provider returned invalid vector data.",
                    status_code=502,
                )
            vectors.append([float(value) for value in embedding])

        if len(vectors) != len(texts):
            raise AppError(
                error="embedding_output_invalid",
                message="Embedding provider returned a mismatched vector count.",
                status_code=502,
                details={"expected": len(texts), "received": len(vectors)},
            )
        return vectors

    def _stub_embedding(self, text: str, *, dimension: int = 16) -> list[float]:
        digest = sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for idx in range(dimension):
            byte = digest[idx % len(digest)]
            values.append((byte / 127.5) - 1.0)
        return values

    def _extract_graph_triplets(self, *, chunks: list[dict[str, Any]], max_triplets: int) -> list[dict[str, Any]]:
        pattern = re.compile(
            r"(?i)\b([A-Z][A-Za-z0-9\-/ ]{2,60}?)\s+(is|are|includes?|contains?|supports?|requires?)\s+([A-Za-z0-9\-/ ,]{2,100})"
        )
        items: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()

        for chunk in chunks:
            text = re.sub(r"\s+", " ", str(chunk.get("content") or "")).strip()
            if not text:
                continue

            for match in pattern.finditer(text):
                subject = match.group(1).strip(" ,.;:")
                predicate = match.group(2).lower().strip()
                obj = match.group(3).strip(" ,.;:")
                key = (subject.lower(), predicate, obj.lower())
                if key in seen:
                    continue
                seen.add(key)
                items.append(
                    {
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "page": chunk.get("page"),
                        "chapter_name": chunk.get("chapter_name"),
                    }
                )
                if len(items) >= max_triplets:
                    return items

        return items
