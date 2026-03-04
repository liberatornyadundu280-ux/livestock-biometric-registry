# Livestock Biometric Registry – Agent Instructions

This repository implements a biometric livestock identification system based on muzzle patterns.

The system uses deep learning embeddings and FAISS vector search to identify cattle.

AI coding agents (Codex) should use this file to understand the architecture and development goals.

---

# Project Goal

Transform this prototype into a scalable livestock biometric registry platform.

Final system architecture:

Client UI → API Server → Biometric Engine → Vector Search → MongoDB Registry

---

# Current Architecture

GUI Layer

- Tkinter interface for authority and farmer dashboards

Core ML Layer

- embedding.py
- Generates 1280-dim embeddings using MobileNetV2

Verification Layer

- verifier.py
- duplicate detection
- livestock verification

Vector Search

- vector_index.py
- FAISS index
- fast similarity search

Database Layer

- database.py
- MongoDB storage

---

# Current Workflow

Registration:

Image → Embedding → Duplicate Check → MongoDB → FAISS Index

Verification:

Image → Embedding → FAISS Search → MongoDB → Result

---

# Development Goals

Agents should gradually refactor the system toward this architecture.

Stage 1 – Stable Backend

- Improve FAISS indexing
- Add batch indexing
- Improve database queries

Stage 2 – API Layer
Convert system to FastAPI backend

Endpoints:

POST /register
POST /verify
GET /livestock/{id}

Stage 3 – Web Interface
Replace Tkinter GUI with web dashboard

Authority panel
Farmer panel

Stage 4 – Scalability
Implement approximate FAISS index (HNSW or IVF)

Stage 5 – Deployment
Docker container
Cloud deployment

---

# Coding Conventions

Python version: 3.10+

Use:
numpy
torch
faiss
pymongo

Guidelines:

- Keep core ML logic inside /core
- Do not mix GUI code with ML logic
- Maintain modular architecture

---

# Important Files

app.py
Application entry point

core/embedding.py
Embedding extraction

core/vector_index.py
FAISS index operations

core/verifier.py
Biometric verification logic

core/database.py
MongoDB operations

gui/
Tkinter interfaces

---

# Testing

Agents should verify:

1. Registration works
2. Duplicate detection works
3. Verification returns correct owner
4. FAISS index updates after registration
