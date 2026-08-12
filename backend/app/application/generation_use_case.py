"""Flashcard / quiz generation use case."""

from __future__ import annotations

from uuid import uuid4

from app.core.errors import AppError
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
from app.ports.retrieval import RetrievalFilters, VectorSearchPort


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
        limit: int = 8,
    ) -> tuple[str, list[str]]:
        subject = await self._subjects.get(user_id=user_id, subject_id=subject_id)
        if subject is None:
            raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")

        search_query = query or f"Key concepts for {subject.name}"
        embedding = (await self._embeddings.embed([search_query]))[0]
        result = await self._retrieval.hybrid_search(
            query_text=search_query,
            query_embedding=embedding,
            filters=RetrievalFilters(
                user_id=user_id,
                subject_id=subject_id,
                document_id=document_id,
            ),
            match_count=limit,
        )
        if not result.chunks:
            # Fallback: take stored chunks if retrieval empty
            chunks = await self._documents.list_chunks(
                user_id=user_id,
                subject_id=subject_id,
                document_id=document_id,
                limit=limit,
            )
            texts = [c.content for c in chunks]
            ids = [c.id for c in chunks]
        else:
            texts = [c.content for c in result.chunks]
            ids = [c.id for c in result.chunks]
        return "\n\n".join(texts), ids

    async def generate_flashcards(
        self,
        *,
        user_id: str,
        subject_id: str,
        count: int = 8,
        query: str | None = None,
        document_id: str | None = None,
        save: bool = True,
    ) -> dict[str, object]:
        context, chunk_ids = await self._context_for_subject(
            user_id=user_id,
            subject_id=subject_id,
            query=query,
            document_id=document_id,
        )
        structured = await self._llm.complete_json(
            messages=[
                ChatCompletionMessage(
                    role="system",
                    content=(
                        "Generate study flashcards as JSON: "
                        '{"cards":[{"front":"...","back":"...","hint":null}]}'
                    ),
                ),
                ChatCompletionMessage(
                    role="user",
                    content=f"Create {count} flashcards from:\n{context}",
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
                    document_id=document_id,
                    artifact_type=ArtifactType.FLASHCARD_DECK,
                    title=query or "Flashcards",
                    status=ArtifactStatus.READY,
                    source_scope=SourceScope.DOCUMENT if document_id else SourceScope.SUBJECT,
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
        difficulty: str | None = "medium",
        save: bool = True,
    ) -> dict[str, object]:
        context, chunk_ids = await self._context_for_subject(
            user_id=user_id,
            subject_id=subject_id,
            query=query,
            document_id=document_id,
        )
        structured = await self._llm.complete_json(
            messages=[
                ChatCompletionMessage(
                    role="system",
                    content=(
                        "Generate a multiple-choice quiz as JSON: "
                        '{"questions":[{"question":"...","options":["A","B","C","D"],'
                        '"correct_option_index":0,"explanation":"..."}]}'
                    ),
                ),
                ChatCompletionMessage(
                    role="user",
                    content=(
                        f"Create {count} {difficulty or 'medium'} questions from:\n{context}"
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
                    document_id=document_id,
                    artifact_type=ArtifactType.QUIZ,
                    title=query or "Quiz",
                    status=ArtifactStatus.READY,
                    source_scope=SourceScope.DOCUMENT if document_id else SourceScope.SUBJECT,
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
