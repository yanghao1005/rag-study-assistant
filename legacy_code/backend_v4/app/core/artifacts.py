from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_json_artifact(*, root_dir: str, run_id: str, name: str, payload: dict[str, Any]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = Path(root_dir) / run_id
    base.mkdir(parents=True, exist_ok=True)
    file_path = base / f"{name}_{timestamp}.json"
    file_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return str(file_path)