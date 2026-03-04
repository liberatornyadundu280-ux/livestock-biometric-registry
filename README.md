# Livestock Biometric Registry (MVP)

A role-based biometric livestock identification prototype for academic demonstration.

The system uses deep embeddings, cosine similarity, FAISS vector search, and MongoDB-backed registry records.

## MVP Scope

- Authority-only livestock registration
- Duplicate detection with hard/soft review
- Multi-angle enrollment (attach additional views to existing livestock ID)
- Authority global search (FOUND / NOT FOUND / INVALID INPUT)
- Farmer scoped verification + global availability check
- Startup health checks (Mongo ping + index enforcement + FAISS/DB count warning)
- Registry reconciliation utility for DB/FAISS drift

## Tech Stack

- Python 3.10+
- Tkinter (UI)
- PyTorch + torchvision (embedding extraction)
- FAISS (vector similarity search)
- MongoDB + pymongo (data layer)

## Current Architecture

`Tkinter UI -> Core ML/Verification -> FAISS Index -> MongoDB`

Core modules:

- `core/embedding.py`: MobileNetV2 embedding extraction
- `core/verifier.py`: duplicate + verification logic
- `core/vector_index.py`: FAISS index build/search/add/rebuild helpers
- `core/database.py`: Mongo operations + index enforcement
- `core/registry_service.py`: transaction-like registration flow with rollback
- `core/reconciliation.py`: DB/FAISS consistency reporting and repair

## Quick Start

1. Ensure MongoDB is running on `mongodb://localhost:27017/`.
2. (Optional) set threshold with env:
   - PowerShell: `$env:BIO_MATCH_THRESHOLD='0.78'`
3. Or edit local `THRESHOLD` file.
4. Run app:

```bash
python app.py
```

## Testing

Unit tests:

```bash
python -m unittest tests.test_stage1_backend -v
```

Integration tests (real Mongo test DB):

```bash
python -m unittest tests.test_stage1_integration -v
```

## Registry Reconciliation Utility

Inspect DB/FAISS consistency:

```bash
python scripts/reconcile_registry.py
```

Repair FAISS from MongoDB:

```bash
python scripts/reconcile_registry.py --repair
```

## Documentation

See [docs/README.md](docs/README.md) for documentation index and evaluator-facing guide.

## Status

MVP ready for academic demonstration.
