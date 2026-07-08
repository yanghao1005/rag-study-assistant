from pathlib import Path

from app.application.use_cases.pipeline_runner import PipelineRunner


def _create_doc(tmp_path: Path) -> str:
    doc = tmp_path / "doc.txt"
    doc.write_text("sample content", encoding="utf-8")
    return str(doc)


def test_pipeline_runner_returns_scaffold_shape(tmp_path: Path) -> None:
    runner = PipelineRunner()
    result = runner.run({"document_id": "doc-1", "file_path": _create_doc(tmp_path)})
    assert result["document_id"] == "doc-1"
    assert "executed_stages" in result
    assert result["output"]["checks_passed"] is True
    assert "checks" in result["stage_results"][0]["details"]


def test_pipeline_runner_writes_artifacts(tmp_path: Path) -> None:
    runner = PipelineRunner(artifacts_dir=str(tmp_path))
    result = runner.run({"document_id": "doc-2", "file_path": _create_doc(tmp_path), "stage": "validate_input"})
    artifact_path = result["stage_results"][0]["details"]["artifact"]
    assert Path(artifact_path).exists()


def test_pipeline_runner_supports_single_stage(tmp_path: Path) -> None:
    runner = PipelineRunner()
    result = runner.run({"document_id": "doc-1", "file_path": _create_doc(tmp_path), "stage": "semantic_chunking"})
    assert result["executed_stages"] == ["semantic_chunking"]


def test_pipeline_runner_supports_stage_range(tmp_path: Path) -> None:
    runner = PipelineRunner()
    result = runner.run(
        {
            "document_id": "doc-1",
            "file_path": _create_doc(tmp_path),
            "from": "parse_document",
            "to": "build_embeddings",
        }
    )
    assert result["executed_stages"] == [
        "parse_document",
        "detect_sections",
        "semantic_chunking",
        "build_embeddings",
    ]


def test_pipeline_runner_rejects_unknown_stage(tmp_path: Path) -> None:
    runner = PipelineRunner()
    try:
        runner.run({"document_id": "doc-1", "file_path": _create_doc(tmp_path), "stage": "unknown_stage"})
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unknown stage" in str(exc)
