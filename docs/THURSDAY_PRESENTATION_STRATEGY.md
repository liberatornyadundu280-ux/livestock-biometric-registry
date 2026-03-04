# Thursday Presentation Strategy

This guide provides a practical script to present the MVP clearly and defensibly.

## 1. Opening (1 minute)

Say:

- "This MVP solves livestock identity and ownership integrity using muzzle biometrics instead of removable tags."
- "The system supports authority registration/search and farmer verification workflows."

## 2. Problem -> Solution Framing (1 minute)

Problem points:

- Tag loss/removal
- Ownership disputes
- Manual record errors

MVP solution:

- Image -> embedding -> FAISS similarity -> threshold decision
- MongoDB-backed registry with role-based access

## 3. Architecture Slide (1 minute)

Show pipeline:

`UI -> Verifier -> FAISS -> MongoDB`

Mention:

- Embedding model: MobileNetV2 features
- Similarity: cosine-based matching
- Duplicate controls: hard/soft review and angle-attach flow

## 4. Live Demo Flow (5-7 minutes)

### Step A: Start clean

- Login as Authority.
- Click `Reset Demo Livestock`.
- Confirm reset success message.

### Step B: Register first livestock

- Select a valid muzzle image.
- Assign owner and register.
- Show success with generated livestock ID.

### Step C: Register angle variant of same animal

- Select different-angle image of same livestock.
- Show duplicate dialog (`HARD` or `SOFT_REVIEW`).
- Choose "Attach as new angle" (Yes).
- Explain no new entity was created.

### Step D: Global search (FOUND)

- Search with an enrolled image.
- Show ID, owner, similarity, confidence.

### Step E: Global search (NOT FOUND)

- Search with non-registered image.
- Show red result + popup alert.

### Step F: Invalid input handling

- Search a clearly poor/invalid image.
- Show `INVALID IMAGE` reason.

### Step G: Farmer view

- Login as Farmer.
- Show own livestock list.
- Run scoped verify and global availability check.

## 5. What Is Production-Ready vs MVP-Only (1 minute)

Clearly state:

- "This is an MVP for demonstration and validation."
- "Next stage adds FastAPI backend, true muzzle detector, and model fine-tuning for stronger angle robustness."

## 6. Likely Questions and Suggested Answers

Q: Why not perfect across all angles?
A: MVP uses pretrained embedding backbone + multi-angle enrollment; full angle robustness requires dedicated metric-learning training and detector stage.

Q: How do you prevent duplicate records?
A: Top-K retrieval + re-ranking + hard/soft duplicate policy + attach-angle workflow.

Q: How do you ensure data/index consistency?
A: Startup checks, unique indexes, transaction-like registration, and reconciliation script.

## 7. Backup Commands (if asked)

Run tests:

```bash
python -m unittest tests.test_stage1_backend -v
python -m unittest tests.test_stage1_integration -v
```

Run reconciliation report:

```bash
python scripts/reconcile_registry.py
python scripts/reconcile_registry.py --repair
```

## 8. Closing Line

"The MVP demonstrates a functioning biometric registry pipeline with role-based operations, duplicate governance, and operational safeguards; the next phase converts this into API-first production architecture."
