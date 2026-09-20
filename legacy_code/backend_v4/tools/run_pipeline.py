from __future__ import annotations

import argparse
import json

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend_v4 pipeline endpoint")
    parser.add_argument("--base-url", default="http://localhost:8000/api", help="API base URL")
    parser.add_argument("--document-id", required=True, help="Document ID")
    parser.add_argument("--stage", default=None, help="Single stage name")
    parser.add_argument("--from-stage", dest="from_stage", default=None, help="Start stage")
    parser.add_argument("--to-stage", dest="to_stage", default=None, help="End stage")
    parser.add_argument("--file-path", required=True, help="PDF/text file path")
    args = parser.parse_args()

    payload: dict[str, object] = {
        "document_id": args.document_id,
        "debug": True,
    }
    if args.stage:
        payload["stage"] = args.stage
    if args.from_stage:
        payload["from"] = args.from_stage
    if args.to_stage:
        payload["to"] = args.to_stage
    payload["file_path"] = args.file_path

    response = httpx.post(f"{args.base_url}/pipeline/run", json=payload, timeout=120.0)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
