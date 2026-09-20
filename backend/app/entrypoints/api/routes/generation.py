"""Generation routes (flashcards / quiz) and study library CRUD."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter

from app.application.generation_use_case import GenerationUseCase
from app.application.study_artifacts import (
    artifact_item_count,
    artifact_origin,
    flashcards_content,
    questions_content,
    study_artifact_title,
)
from app.core.errors import AppError
from app.domain.entities.enums import ArtifactStatus, ArtifactType, QuestionType, SourceScope
from app.domain.entities.study import Flashcard, QuizQuestion, StudyArtifact
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import (
    CreateArtifactRequest,
    FlashcardWriteRequest,
    GenerateFlashcardsRequest,
    GenerateQuizRequest,
    QuizQuestionWriteRequest,
    UpdateArtifactRequest,
)

router = APIRouter(prefix="/generate", tags=["generate"])


def _generation_use_case(container: ContainerDep) -> GenerationUseCase:
    return GenerationUseCase(
        subjects=container.subjects,
        documents=container.documents,
        study=container.study,
        retrieval=container.retrieval,
        embeddings=container.embeddings,
        llm=container.llm,
    )


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _artifact_summary(artifact: StudyArtifact) -> dict[str, object]:
    return {
        "id": artifact.id,
        "artifact_type": artifact.artifact_type.value,
        "title": artifact.title,
        "status": artifact.status.value,
        "subject_id": artifact.subject_id,
        "created_at": _iso(artifact.created_at),
        "updated_at": _iso(artifact.updated_at or artifact.created_at),
        "item_count": artifact_item_count(artifact),
        "origin": artifact_origin(artifact.metadata),
    }


def _card_payload(card: Flashcard) -> dict[str, object]:
    return {"id": card.id, "front": card.front, "back": card.back, "hint": card.hint}


def _question_payload(question: QuizQuestion) -> dict[str, object]:
    return {
        "id": question.id,
        "question": question.question,
        "options": question.options,
        "correct_option_index": question.correct_option_index,
        "explanation": question.explanation,
    }


async def _require_subject(container: ContainerDep, *, user_id: str, subject_id: str) -> None:
    subject = await container.subjects.get(user_id=user_id, subject_id=subject_id)
    if subject is None:
        raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")


async def _require_artifact(
    container: ContainerDep, *, user_id: str, artifact_id: str
) -> StudyArtifact:
    artifact = await container.study.get_artifact(user_id=user_id, artifact_id=artifact_id)
    if artifact is None:
        raise AppError(status_code=404, error="artifact_not_found", message="Artifact not found.")
    return artifact


async def _sync_flashcards(
    container: ContainerDep, *, user_id: str, artifact: StudyArtifact
) -> StudyArtifact:
    cards = await container.study.list_flashcards(user_id=user_id, artifact_id=artifact.id)
    artifact.content_json = flashcards_content(cards)
    return await container.study.update_artifact(artifact)


async def _sync_questions(
    container: ContainerDep, *, user_id: str, artifact: StudyArtifact
) -> StudyArtifact:
    questions = await container.study.list_quiz_questions(
        user_id=user_id, artifact_id=artifact.id
    )
    artifact.content_json = questions_content(questions)
    return await container.study.update_artifact(artifact)


def _clean_hint(hint: str | None) -> str | None:
    if hint is None:
        return None
    cleaned = hint.strip()
    return cleaned or None


@router.post("/flashcards")
async def generate_flashcards(
    body: GenerateFlashcardsRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    return await _generation_use_case(container).generate_flashcards(
        user_id=user.id,
        subject_id=body.subject_id,
        count=body.count,
        query=body.query,
        document_id=body.document_id,
        document_ids=body.document_ids,
        save=body.save,
    )


@router.post("/quiz")
async def generate_quiz(
    body: GenerateQuizRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    return await _generation_use_case(container).generate_quiz(
        user_id=user.id,
        subject_id=body.subject_id,
        count=body.count,
        query=body.query,
        document_id=body.document_id,
        document_ids=body.document_ids,
        difficulty=body.difficulty,
        save=body.save,
    )


@router.get("/artifacts")
async def list_artifacts(
    user: CurrentUserDep,
    container: ContainerDep,
    subject_id: str,
    artifact_type: str | None = None,
) -> dict[str, object]:
    items = await container.study.list_artifacts(
        user_id=user.id,
        subject_id=subject_id,
        artifact_type=artifact_type,
    )
    return {"items": [_artifact_summary(item) for item in items]}


@router.post("/artifacts", status_code=201)
async def create_artifact(
    body: CreateArtifactRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    await _require_subject(container, user_id=user.id, subject_id=body.subject_id)
    kind = "quiz" if body.artifact_type == "quiz" else "flashcards"
    artifact = await container.study.create_artifact(
        StudyArtifact(
            id=str(uuid4()),
            user_id=user.id,
            subject_id=body.subject_id,
            artifact_type=ArtifactType(body.artifact_type),
            title=(
                body.title.strip()
                if body.title and body.title.strip()
                else study_artifact_title(None, kind=kind)
            ),
            status=ArtifactStatus.READY,
            source_scope=SourceScope.SUBJECT,
            content_json=(
                {"cards": []} if body.artifact_type == "flashcard_deck" else {"questions": []}
            ),
            metadata={"origin": body.origin},
        )
    )
    if body.artifact_type == "flashcard_deck" and body.cards:
        cards: list[Flashcard] = []
        for index, raw in enumerate(body.cards):
            if not isinstance(raw, dict):
                continue
            front = str(raw.get("front") or "").strip()
            back = str(raw.get("back") or "").strip()
            if not front or not back:
                continue
            cards.append(
                Flashcard(
                    id=str(uuid4()),
                    user_id=user.id,
                    artifact_id=artifact.id,
                    front=front,
                    back=back,
                    hint=_clean_hint(str(raw["hint"]) if raw.get("hint") is not None else None),
                    position=index,
                )
            )
        if cards:
            await container.study.save_flashcards(cards)
            artifact = await _sync_flashcards(container, user_id=user.id, artifact=artifact)
    elif body.artifact_type == "quiz" and body.questions:
        questions: list[QuizQuestion] = []
        for index, raw in enumerate(body.questions):
            if not isinstance(raw, dict):
                continue
            text = str(raw.get("question") or "").strip()
            options = raw.get("options") or []
            if not text or not isinstance(options, list) or len(options) < 2:
                continue
            questions.append(
                QuizQuestion(
                    id=str(uuid4()),
                    user_id=user.id,
                    artifact_id=artifact.id,
                    question=text,
                    options=[str(opt) for opt in options],
                    correct_option_index=int(raw.get("correct_option_index") or 0),
                    explanation=_clean_hint(
                        str(raw["explanation"]) if raw.get("explanation") is not None else None
                    ),
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    position=index,
                )
            )
        if questions:
            await container.study.save_quiz_questions(questions)
            artifact = await _sync_questions(container, user_id=user.id, artifact=artifact)
    return _artifact_summary(artifact)


@router.get("/artifacts/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    payload: dict[str, object] = {
        **_artifact_summary(artifact),
        "content_json": artifact.content_json,
    }
    if artifact.artifact_type.value == "flashcard_deck":
        cards = await container.study.list_flashcards(user_id=user.id, artifact_id=artifact_id)
        payload["cards"] = [_card_payload(card) for card in cards]
        payload["item_count"] = len(cards)
    elif artifact.artifact_type.value == "quiz":
        questions = await container.study.list_quiz_questions(
            user_id=user.id, artifact_id=artifact_id
        )
        payload["questions"] = [_question_payload(item) for item in questions]
        payload["item_count"] = len(questions)
    return payload


@router.patch("/artifacts/{artifact_id}")
async def update_artifact(
    artifact_id: str,
    body: UpdateArtifactRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    if body.title is not None:
        artifact.title = body.title.strip()
        if not artifact.title:
            raise AppError(status_code=400, error="invalid_title", message="Title is required.")
    artifact = await container.study.update_artifact(artifact)
    return _artifact_summary(artifact)


@router.delete("/artifacts/{artifact_id}")
async def delete_artifact(
    artifact_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    deleted = await container.study.delete_artifact(user_id=user.id, artifact_id=artifact_id)
    return {"deleted": deleted}


@router.post("/artifacts/{artifact_id}/flashcards", status_code=201)
async def add_flashcard(
    artifact_id: str,
    body: FlashcardWriteRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    if artifact.artifact_type.value != "flashcard_deck":
        raise AppError(
            status_code=400, error="wrong_artifact_type", message="Not a flashcard deck."
        )
    existing = await container.study.list_flashcards(user_id=user.id, artifact_id=artifact_id)
    card = Flashcard(
        id=str(uuid4()),
        user_id=user.id,
        artifact_id=artifact_id,
        front=body.front.strip(),
        back=body.back.strip(),
        hint=_clean_hint(body.hint),
        position=len(existing),
    )
    await container.study.save_flashcards([card])
    await _sync_flashcards(container, user_id=user.id, artifact=artifact)
    return _card_payload(card)


@router.patch("/artifacts/{artifact_id}/flashcards/{card_id}")
async def update_flashcard(
    artifact_id: str,
    card_id: str,
    body: FlashcardWriteRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    card = await container.study.get_flashcard(user_id=user.id, flashcard_id=card_id)
    if card is None or card.artifact_id != artifact_id:
        raise AppError(
            status_code=404, error="flashcard_not_found", message="Flashcard not found."
        )
    card.front = body.front.strip()
    card.back = body.back.strip()
    card.hint = _clean_hint(body.hint)
    updated = await container.study.update_flashcard(card)
    await _sync_flashcards(container, user_id=user.id, artifact=artifact)
    return _card_payload(updated)


@router.delete("/artifacts/{artifact_id}/flashcards/{card_id}")
async def delete_flashcard(
    artifact_id: str,
    card_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    card = await container.study.get_flashcard(user_id=user.id, flashcard_id=card_id)
    if card is None or card.artifact_id != artifact_id:
        raise AppError(
            status_code=404, error="flashcard_not_found", message="Flashcard not found."
        )
    deleted = await container.study.delete_flashcard(user_id=user.id, flashcard_id=card_id)
    await _sync_flashcards(container, user_id=user.id, artifact=artifact)
    return {"deleted": deleted}


@router.post("/artifacts/{artifact_id}/questions", status_code=201)
async def add_quiz_question(
    artifact_id: str,
    body: QuizQuestionWriteRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    if artifact.artifact_type.value != "quiz":
        raise AppError(status_code=400, error="wrong_artifact_type", message="Not a quiz.")
    options = [opt.strip() for opt in body.options if opt.strip()]
    if body.correct_option_index >= len(options):
        raise AppError(
            status_code=400,
            error="invalid_correct_option",
            message="Correct option is out of range.",
        )
    existing = await container.study.list_quiz_questions(user_id=user.id, artifact_id=artifact_id)
    question = QuizQuestion(
        id=str(uuid4()),
        user_id=user.id,
        artifact_id=artifact_id,
        question=body.question.strip(),
        options=options,
        correct_option_index=body.correct_option_index,
        explanation=_clean_hint(body.explanation),
        question_type=QuestionType.MULTIPLE_CHOICE,
        position=len(existing),
    )
    await container.study.save_quiz_questions([question])
    await _sync_questions(container, user_id=user.id, artifact=artifact)
    return _question_payload(question)


@router.patch("/artifacts/{artifact_id}/questions/{question_id}")
async def update_quiz_question(
    artifact_id: str,
    question_id: str,
    body: QuizQuestionWriteRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    question = await container.study.get_quiz_question(user_id=user.id, question_id=question_id)
    if question is None or question.artifact_id != artifact_id:
        raise AppError(status_code=404, error="question_not_found", message="Question not found.")
    options = [opt.strip() for opt in body.options if opt.strip()]
    if body.correct_option_index >= len(options):
        raise AppError(
            status_code=400,
            error="invalid_correct_option",
            message="Correct option is out of range.",
        )
    question.question = body.question.strip()
    question.options = options
    question.correct_option_index = body.correct_option_index
    question.explanation = _clean_hint(body.explanation)
    updated = await container.study.update_quiz_question(question)
    await _sync_questions(container, user_id=user.id, artifact=artifact)
    return _question_payload(updated)


@router.delete("/artifacts/{artifact_id}/questions/{question_id}")
async def delete_quiz_question(
    artifact_id: str,
    question_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await _require_artifact(container, user_id=user.id, artifact_id=artifact_id)
    question = await container.study.get_quiz_question(user_id=user.id, question_id=question_id)
    if question is None or question.artifact_id != artifact_id:
        raise AppError(status_code=404, error="question_not_found", message="Question not found.")
    deleted = await container.study.delete_quiz_question(user_id=user.id, question_id=question_id)
    await _sync_questions(container, user_id=user.id, artifact=artifact)
    return {"deleted": deleted}
