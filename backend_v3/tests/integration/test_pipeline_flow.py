from app.application.pipeline_runner import PipelineRunner
from app.domain.pipeline import PipelineRunRequest


def test_full_pipeline_summary_flow() -> None:
    runner = PipelineRunner()
    request = PipelineRunRequest(
        document_id="doc-int-1",
        user_id="user-int-1",
        subject_id="subject-int-1",
        document_type="summary",
        document_text="Chapter 1: Intro to Networks. TCP and UDP are transport protocols.",
        query="What are transport protocols?",
    )

    result = runner.run(request)

    assert len(result.executed_stages) == 9
    assert result.output["query"] == "What are transport protocols?"
    assert "sources" in result.output
