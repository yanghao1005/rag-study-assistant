from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_artifact(*, root_dir: str, run_id: str, name: str, payload: dict[str, Any]) -> str:
    root = Path(root_dir)
    target = root / run_id
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{name}.json"
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return str(path)
