import argparse
import json

from app.application.pipeline_runner import PipelineRunner
from app.domain.pipeline import PipelineRunRequest, PipelineStage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run backend_v3 pipeline stages")
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--user-id")
    parser.add_argument("--subject-id")
    parser.add_argument("--query", default="summarize the document")
    parser.add_argument("--document-text", default="")
    parser.add_argument("--file-path")
    parser.add_argument("--document-type", choices=["pdf", "summary"], default="summary")
    parser.add_argument("--stage", choices=[stage.value for stage in PipelineStage])
    parser.add_argument("--from", dest="from_stage", choices=[stage.value for stage in PipelineStage])
    parser.add_argument("--to", dest="to_stage", choices=[stage.value for stage in PipelineStage])
    parser.add_argument("--debug", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    payload = PipelineRunRequest(
        document_id=args.document_id,
        user_id=args.user_id,
        subject_id=args.subject_id,
        query=args.query,
        document_text=args.document_text,
        file_path=args.file_path,
        document_type=args.document_type,
        stage=PipelineStage(args.stage) if args.stage else None,
        **({"from": PipelineStage(args.from_stage)} if args.from_stage else {}),
        **({"to": PipelineStage(args.to_stage)} if args.to_stage else {}),
        debug=args.debug,
    )

    runner = PipelineRunner()
    result = runner.run(payload)
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
