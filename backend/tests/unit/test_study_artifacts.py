from app.application.study_artifacts import (
    artifact_item_count,
    artifact_origin,
    study_artifact_title,
)
from app.domain.entities.enums import ArtifactType
from app.domain.entities.study import StudyArtifact


def test_study_artifact_title_uses_query() -> None:
    assert study_artifact_title("  BMC  y valor ", kind="flashcards") == "BMC y valor"


def test_study_artifact_title_truncates() -> None:
    title = study_artifact_title("x" * 120, kind="quiz")
    assert len(title) == 80


def test_study_artifact_title_fallback_includes_kind() -> None:
    flash = study_artifact_title(None, kind="flashcards")
    quiz = study_artifact_title("   ", kind="quiz")
    assert flash.startswith("Flashcards · ")
    assert quiz.startswith("Quiz · ")


def test_artifact_origin_and_count() -> None:
    artifact = StudyArtifact(
        id="a1",
        user_id="u1",
        subject_id="s1",
        artifact_type=ArtifactType.FLASHCARD_DECK,
        title="BMC",
        content_json={"cards": [{}, {}]},
        metadata={"origin": "manual"},
    )
    assert artifact_origin(artifact.metadata) == "manual"
    assert artifact_item_count(artifact) == 2
    assert artifact_origin({}) == "generated"
