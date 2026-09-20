import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.config import get_settings


def persist_debug_artifact(kind: str, payload: dict[str, Any], trace_id: str | None = None) -> tuple[str, str]:
    settings = get_settings()
    trace_value = trace_id or f"{kind}-{uuid4().hex[:12]}"

    debug_dir = Path(settings.debug_artifacts_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    file_name = f"{kind}_{trace_value}_{timestamp}.json"
    target_file = debug_dir / file_name
    target_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return trace_value, str(target_file)
