# legacy_code

This folder is reserved for archived prototype code that is no longer part of the active implementation baseline.

Active baseline for development:

- `backend_v5`
- `frontend_v2`

Legacy candidates to archive:

- `backend`
- `backend_v2`
- `backend_v3`
- `backend_v4`
- `frontend`

To archive them in one step, run:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\archive-legacy-code.ps1"
```

Notes:

- The script is idempotent.
- Existing archived folders are not overwritten; they are skipped.
- Use git to review and commit moves after execution.

