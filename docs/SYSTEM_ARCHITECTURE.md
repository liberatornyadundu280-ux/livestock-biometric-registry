# System Architecture

## 1. Architecture Overview

The system follows a modular layered design:

- GUI Layer (Tkinter-based multi-screen interface)
- Core ML Engine (Embedding & Verification Logic)
- Database Layer (JSON-based storage)
- Role-Based Access Control Layer

---

## 2. Embedding Generation

- Backbone: MobileNetV2 (pretrained on ImageNet)
- Output: 1280-dimensional embedding
- Normalization: L2 normalization
- Similarity Metric: Cosine similarity

---

## 3. Duplicate Detection

During registration:

1. Generate embedding.
2. Compare against all stored embeddings.
3. If similarity ≥ 0.85 → duplicate alert.
4. Authority may override.

---

## 4. Verification Modes

### Farmer Verification

- Scoped to farmer's own livestock.
- Prevents cross-tenant data exposure.

### Authority Global Search

- Searches entire registry.
- Returns livestock ID and owner information.

---

## 5. Data Model

### Farmers

- farmer_id
- username
- password
- livestock_ids

### Livestock

- livestock_id
- livestock_type
- biometric_type
- owner_id
- owner_name
- embedding (1280-d float vector)
