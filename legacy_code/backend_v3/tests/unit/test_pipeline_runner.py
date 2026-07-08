from app.application.pipeline_runner import PipelineRunner
from app.domain.pipeline import PipelineRunRequest


def test_run_single_stage_parse_document() -> None:
    runner = PipelineRunner()
    request = PipelineRunRequest(
        document_id="doc-1",
        document_text="Hello world",
        stage="parse_document",
    )
    result = runner.run(request)
    assert len(result.executed_stages) == 1
    assert result.executed_stages[0].value == "parse_document"
    assert result.stage_results[0].details["total_pages"] == 1
