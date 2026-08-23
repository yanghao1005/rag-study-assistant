"""Flashcard / quiz generation use case."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from app.application.retrieval_policy import (
    build_index_context,
    format_context_blocks,
    generation_search_query,
    is_course_admin_text,
    merge_with_opening_chunks,
    select_documents_for_generation,
)
from app.core.errors import AppError
from app.domain.entities.document import DocumentChunk
from app.domain.entities.enums import (
    ArtifactStatus,
    ArtifactType,
    Difficulty,
    QuestionType,
    SourceScope,
)
from app.domain.entities.study import Flashcard, QuizQuestion, StudyArtifact
from app.ports.llm import ChatCompletionMessage, EmbeddingPort, LLMPort
from app.ports.repositories import (
    DocumentRepositoryPort,
    StudyRepositoryPort,
    SubjectRepositoryPort,
)
from app.ports.retrieval import HybridRetrievalResult, RetrievalFilters, VectorSearchPort

_FLASHCARD_SYSTEM = (
    "You create active-recall flashcards for exam revision of the SUBJECT MATTER. "
    'Return JSON: {"cards":[{"front":"...","back":"...","hint":null}]}. '
    "Each card tests one concept, definition, framework, process, formula or comparison "
    "that a student must remember from the notes. "
    "Front is a short question; back is the answer from the notes. "
    "Use the same language as the source text. "
    "FORBIDDEN topics: course logistics, grading/how the course is evaluated, ECTS, "
    "schedule, teacher, deadlines, syllabus meta, 'what this course is about', "
    "or copying learning-outcome lists from the course presentation. "
    "If the context mixes a course guide with lecture notes, ignore the guide."
)
_QUIZ_SYSTEM = (
    "You create a multiple-choice quiz for exam revision of the SUBJECT MATTER. "
    'Return JSON: {"questions":[{"question":"...","options":["A","B","C","D"],'
    '"correct_option_index":0,"explanation":"..."}]}. '
    "Each item tests a concept, model, process or comparison from the lecture notes. "
    "FORBIDDEN: course logistics, grading of the course, ECTS, schedule, teacher, "
    "deadlines, or syllabus meta from the course presentation. "
    "Use the same language as the source text."
)


class GenerationUseCase:
    def __init__(
        self,
        *,
        subjects: SubjectRepositoryPort,
        documents: DocumentRepositoryPort,
        study: StudyRepositoryPort,
        retrieval: VectorSearchPort,
        embeddings: EmbeddingPort,
        llm: LLMPort,
    ) -> None:
        self._subjects = subjects
        self._documents = documents
        self._study = study
        self._retrieval = retrieval
        self._embeddings = embeddings
        self._llm = llm

    async def _context_for_subject(
        self,
        *,
        user_id: str,
        subject_id: str,
        query: str | None,
        document_id: str | None,
        document_ids: list[str] | None = None,
        limit: int = 12,
    ) -> tuple[str, list[str], str | None]:
        subject = await self._subjects.get(user_id=user_id, subject_id=subject_id)
        if subject is None:
            raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")

        requested = RetrievalFilters(
            user_id=user_id,
            subject_id=subject_id,
            document_id=document_id,
            document_ids=tuple(document_ids or ()),
        )
        all_docs = await self._documents.list_for_subject(user_id=user_id, subject_id=subject_id)
        requested_ids = requested.resolved_document_ids()
        docs = select_documents_for_generation(all_docs, scoped_ids=requested_ids)
        study_ids = tuple(document.id for document in docs)
        filters = RetrievalFilters(
            user_id=user_id,
            subject_id=subject_id,
            document_id=document_id if requested_ids else None,
            document_ids=tuple(document_ids or ()) if requested_ids else (),
        )
        scoped_document_id = study_ids[0] if len(study_ids) == 1 else None

        search_query = generation_search_query(subject.name, query)
        embedding = (await self._embeddings.embed([search_query]))[0]
        result = await self._retrieval.hybrid_search(
            query_text=search_query,
            query_embedding=embedding,
            filters=filters,
            match_count=max(limit, 16),
        )
        if not requested_ids and docs:
            allowed = {item.id for item in docs}
            result = HybridRetrievalResult(
                chunks=[chunk for chunk in result.chunks if chunk.document_id in allowed],
                dense_ids=result.dense_ids,
                lexical_ids=result.lexical_ids,
            )
        if study_ids:
            openings = await self._opening_chunks(
                user_id=user_id,
                subject_id=subject_id,
                document_ids=list(study_ids),
                per_document=2,
            )
            result = merge_with_opening_chunks(
                result, openings, per_document=2, limit=limit
            )
        if not result.chunks:
            fallback = await self._fallback_chunks(
                user_id=user_id,
                subject_id=subject_id,
                scoped=study_ids,
                limit=limit,
            )
            texts = [chunk.content for chunk in fallback]
            ids = [chunk.id for chunk in fallback]
            return "\n\n".join(texts), ids, scoped_document_id

        index_block = build_index_context(
            docs or all_docs,
            retrieved_ids={chunk.document_id for chunk in result.chunks},
            include_all=True,
        )
        context = format_context_blocks(result.chunks, docs or all_docs)
        combined = f"{index_block}\n\n{context}" if index_block else context
        return combined, [chunk.id for chunk in result.chunks], scoped_document_id

    async def _opening_chunks(
        self,
        *,
        user_id: str,
        subject_id: str,
        document_ids: list[str],
        per_document: int,
    ) -> list[DocumentChunk]:
        if not document_ids:
            return []

        async def load(document_id: str) -> list[DocumentChunk]:
            return await self._documents.list_chunks(
                user_id=user_id,
                subject_id=subject_id,
                document_id=document_id,
                limit=per_document,
            )

        parts = await asyncio.gather(*[load(doc_id) for doc_id in document_ids])
        chunks: list[DocumentChunk] = []
        for part in parts:
            chunks.extend(part)
        return chunks

    async def _fallback_chunks(
        self,
        *,
        user_id: str,
        subject_id: str,
        scoped: tuple[str, ...],
        limit: int,
    ) -> list[DocumentChunk]:
        if not scoped:
            return await self._documents.list_chunks(
                user_id=user_id,
                subject_id=subject_id,
                limit=limit,
            )
        chunks = []
        remaining = limit
        for document_id in scoped:
            if remaining <= 0:
                break
            part = await self._documents.list_chunks(
                user_id=user_id,
                subject_id=subject_id,
                document_id=document_id,
                limit=remaining,
            )
            chunks.extend(part)
            remaining = limit - len(chunks)
        return chunks

    async def generate_flashcards(
        self,
        *,
        user_id: str,
        subject_id: str,
        count: int = 8,
        query: str | None = None,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        save: bool = True,
    ) -> dict[str, object]:
        context, chunk_ids, scoped_document_id = await self._context_for_subject(
            user_id=user_id,
            subject_id=subject_id,
            query=query,
            document_id=document_id,
            document_ids=document_ids,
        )
        structured = await self._llm.complete_json(
            messages=[
                ChatCompletionMessage(role="system", content=_FLASHCARD_SYSTEM),
                ChatCompletionMessage(
                    role="user",
                    content=(
                        f"Create {count} flashcards for active recall of the lecture notes.\n"
                        f"{context}"
                    ),
                ),
            ],
            schema_name="flashcards",
        )
        raw_cards = structured.data.get("cards") or []
        cards_payload = []
        for item in raw_cards[:count]:
            if not isinstance(item, dict):
                continue
            front = str(item.get("front") or "").strip()
            back = str(item.get("back") or "").strip()
            if not front or not back:
                continue
            if is_course_admin_text(f"{front}\n{back}"):
                continue
            cards_payload.append(
                {
                    "front": front,
                    "back": back,
                    "hint": item.get("hint"),
                    "source_chunk_ids": chunk_ids[:3],
                }
            )

        artifact_id = None
        if save and cards_payload:
            artifact = await self._study.create_artifact(
                StudyArtifact(
                    id=str(uuid4()),
                    user_id=user_id,
                    subject_id=subject_id,
                    document_id=scoped_document_id,
                    artifact_type=ArtifactType.FLASHCARD_DECK,
                    title=query or "Flashcards",
                    status=ArtifactStatus.READY,
                    source_scope=(
                        SourceScope.DOCUMENT if scoped_document_id else SourceScope.SUBJECT
                    ),
                    content_json={"cards": cards_payload},
                )
            )
            artifact_id = artifact.id
            flashcards: list[Flashcard] = []
            for index, card in enumerate(cards_payload):
                hint_raw = card.get("hint")
                source_raw = card.get("source_chunk_ids") or []
                flashcards.append(
                    Flashcard(
                        id=str(uuid4()),
                        user_id=user_id,
                        artifact_id=artifact.id,
                        front=str(card["front"]),
                        back=str(card["back"]),
                        hint=str(hint_raw) if hint_raw is not None else None,
                        source_chunk_ids=[str(cid) for cid in source_raw]
                        if isinstance(source_raw, list)
                        else [],
                        position=index,
                    )
                )
            await self._study.save_flashcards(flashcards)

        return {
            "artifact_id": artifact_id,
            "cards": cards_payload,
            "model": structured.model,
            "usage": structured.usage,
        }

    async def generate_quiz(
        self,
        *,
        user_id: str,
        subject_id: str,
        count: int = 5,
        query: str | None = None,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        difficulty: str | None = "medium",
        save: bool = True,
    ) -> dict[str, object]:
        context, chunk_ids, scoped_document_id = await self._context_for_subject(
            user_id=user_id,
            subject_id=subject_id,
            query=query,
            document_id=document_id,
            document_ids=document_ids,
        )
        structured = await self._llm.complete_json(
            messages=[
                ChatCompletionMessage(role="system", content=_QUIZ_SYSTEM),
                ChatCompletionMessage(
                    role="user",
                    content=(
                        f"Create {count} {difficulty or 'medium'} questions "
                        f"about the lecture notes, not the course guide.\n{context}"
                    ),
                ),
            ],
            schema_name="quiz",
        )
        raw_questions = structured.data.get("questions") or []
        questions_payload = []
        for item in raw_questions[:count]:
            if not isinstance(item, dict):
                continue
            question = str(item.get("question") or "").strip()
            options = item.get("options") or []
            if not question or not isinstance(options, list) or len(options) < 2:
                continue
            if is_course_admin_text(question):
                continue
            questions_payload.append(
                {
                    "question": question,
                    "options": [str(o) for o in options],
                    "correct_option_index": int(item.get("correct_option_index") or 0),
                    "explanation": item.get("explanation"),
                    "source_chunk_ids": chunk_ids[:3],
                }
            )

        artifact_id = None
        if save and questions_payload:
            artifact = await self._study.create_artifact(
                StudyArtifact(
                    id=str(uuid4()),
                    user_id=user_id,
                    subject_id=subject_id,
                    document_id=scoped_document_id,
                    artifact_type=ArtifactType.QUIZ,
                    title=query or "Quiz",
                    status=ArtifactStatus.READY,
                    source_scope=(
                        SourceScope.DOCUMENT if scoped_document_id else SourceScope.SUBJECT
                    ),
                    content_json={"questions": questions_payload},
                )
            )
            artifact_id = artifact.id
            diff = Difficulty(difficulty) if difficulty in {"easy", "medium", "hard"} else None
            quiz_questions: list[QuizQuestion] = []
            for index, q in enumerate(questions_payload):
                options_raw = q["options"]
                options = (
                    [str(opt) for opt in options_raw]
                    if isinstance(options_raw, list)
                    else []
                )
                explanation_raw = q.get("explanation")
                source_raw = q.get("source_chunk_ids") or []
                correct_raw = q["correct_option_index"]
                correct_option_index = (
                    int(correct_raw)
                    if isinstance(correct_raw, int | str)
                    else 0
                )
                quiz_questions.append(
                    QuizQuestion(
                        id=str(uuid4()),
                        user_id=user_id,
                        artifact_id=artifact.id,
                        question=str(q["question"]),
                        options=options,
                        correct_option_index=correct_option_index,
                        explanation=(
                            str(explanation_raw) if explanation_raw is not None else None
                        ),
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        difficulty=diff,
                        source_chunk_ids=[str(cid) for cid in source_raw]
                        if isinstance(source_raw, list)
                        else [],
                        position=index,
                    )
                )
            await self._study.save_quiz_questions(quiz_questions)

        return {
            "artifact_id": artifact_id,
            "questions": questions_payload,
            "model": structured.model,
            "usage": structured.usage,
        }
