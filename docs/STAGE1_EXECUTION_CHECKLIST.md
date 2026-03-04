# Stage 1 Execution Checklist (Stable Backend)

This checklist operationalizes `docs/AGENTS.md` Stage 1 goals for the current codebase.

## Scope

- Improve FAISS indexing behavior
- Add backend validation tests for critical workflow behaviors
- Validate core database query paths used by registration and verification

## Acceptance Criteria from AGENTS

1. Registration works
2. Duplicate detection works
3. Verification returns correct owner
4. FAISS index updates after registration

## Implemented Verification Suite

- File: `tests/test_stage1_backend.py`
- Framework: `unittest` (standard library)
- Tests included:
  - `test_registration_writes_record`
  - `test_duplicate_detection_works`
  - `test_global_verification_returns_owner`
  - `test_faiss_index_updates_after_add`

- File: `tests/test_stage1_integration.py` (real MongoDB integration)
- Integration tests included:
  - `test_register_transaction_writes_db_and_faiss`
  - `test_append_gallery_reflects_in_rebuild`
  - `test_transaction_rolls_back_on_faiss_failure`

## Run Commands

```bash
python -m unittest tests.test_stage1_backend -v
python -m unittest tests.test_stage1_integration -v
python scripts/reconcile_registry.py
python scripts/reconcile_registry.py --repair
```

Optional broader sanity check:

```bash
python -m compileall -q app.py core gui
```

## Current Stage 1 Status

- [x] MongoDB-backed registration path in active app flow
- [x] FAISS index rebuild reset behavior in `core/vector_index.py`
- [x] Duplicate detection returns owner metadata
- [x] Backend tests for AGENTS acceptance criteria
- [x] Batch indexing API surface (`add_vectors`) in `core/vector_index.py`
- [x] MongoDB index strategy with startup enforcement (`ensure_indexes`)
- [x] Backend registration transaction flow with rollback on FAISS failure (`core/registry_service.py`)

## Next Stage 1 Hardening Tasks

1. Stage 1 hardening complete. Next move: Stage 2 API migration.
