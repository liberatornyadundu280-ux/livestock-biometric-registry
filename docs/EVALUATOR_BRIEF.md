# Evaluator Brief (MVP)

This brief helps evaluators quickly assess the Livestock Biometric Registry MVP.

## 1. What This MVP Demonstrates

- Role-based livestock biometric workflows
- Authority-controlled livestock registration
- Duplicate prevention with review policy
- Farmer-scoped verification and global availability checks
- MongoDB + FAISS operational consistency safeguards

## 2. Core Technical Flow

Registration:

`Image -> Embedding -> Duplicate Check -> MongoDB -> FAISS`

Verification:

`Image -> Embedding -> FAISS Candidate Search -> Re-ranking -> Decision`

## 3. Evaluation Focus Areas

1. Functional correctness
- Registration produces valid livestock IDs
- Duplicate alerts trigger for same-cow angle variants
- Global search returns FOUND/NOT FOUND correctly

2. Access control
- Farmer cannot register livestock
- Farmer operations are scoped and limited

3. Reliability safeguards
- Startup DB/index checks
- Not-found and invalid-input user alerts
- Transaction-like registration rollback on FAISS failure
- Reconciliation utility for DB/FAISS drift

## 4. Suggested Live Checks

1. Start app and confirm no startup errors.
2. Authority: register one livestock image.
3. Authority: register different-angle image of same animal and use attach-angle option.
4. Authority: run one FOUND search and one NOT FOUND search.
5. Farmer: login, verify scoped lookup, run global availability check.
6. Run reconciliation report:

```bash
python scripts/reconcile_registry.py
```

## 5. Commands for Technical Verification

```bash
python -m unittest tests.test_stage1_backend -v
python -m unittest tests.test_stage1_integration -v
```

## 6. Known MVP Boundaries (Explicit)

- Uses pretrained embedding backbone; not fully fine-tuned for all angle extremes.
- Input validation includes practical quality gates, not a dedicated production-grade muzzle detector.
- API-first production architecture (FastAPI/Web) is planned for next phase.

## 7. Verdict Framing

If workflows execute correctly with the above checks, this MVP satisfies academic demonstration goals for:

- biometric registry feasibility
- role-based operation
- duplicate governance
- backend consistency controls
