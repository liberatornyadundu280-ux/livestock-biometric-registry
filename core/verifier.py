import numpy as np

from core.vector_index import search_embedding
from core.database import get_farmer_by_id, get_farmer_livestock, get_livestock_by_id
from core.embedding import get_embedding_list
from core.input_validator import validate_biometric_input


# ---------------------------------
# Cosine Similarity
# ---------------------------------

def cosine_similarity(vec1, vec2):

    vec1 = np.array(vec1, dtype=np.float32)
    vec2 = np.array(vec2, dtype=np.float32)

    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(vec1, vec2) / denom)


def get_confidence_label(similarity, threshold, margin=0.05):
    """
    Classify match confidence around threshold for UI messaging.
    """
    if similarity >= threshold + margin:
        return "HIGH"
    if similarity >= threshold:
        return "BORDERLINE"
    return "LOW"


def _record_embeddings(record):
    if not record:
        return []

    if "embedding_gallery" in record and isinstance(record["embedding_gallery"], list):
        return record["embedding_gallery"]

    if "embedding" in record and isinstance(record["embedding"], list):
        return [record["embedding"]]

    return []


# ---------------------------------
# Duplicate Detection (Registration)
# ---------------------------------

def check_duplicate(embedding, threshold=0.78):

    embedding = np.array(embedding, dtype=np.float32)

    # Top-K ANN retrieval followed by exact reranking on candidate galleries.
    results = search_embedding(embedding, k=10)

    if len(results) == 0:
        return {
            "duplicate": False
        }

    soft_threshold = max(0.68, threshold - 0.10)

    candidate_ids = []
    for livestock_id, _ in results:
        if livestock_id not in candidate_ids:
            candidate_ids.append(livestock_id)

    best_id = None
    best_score = -1.0
    best_owner_name = "Unknown"

    for livestock_id in candidate_ids:
        record = get_livestock_by_id(livestock_id)
        if not record:
            continue

        owner_name = record.get("owner_name", "Unknown")
        for stored in _record_embeddings(record):
            score = cosine_similarity(embedding, stored)
            if score > best_score:
                best_score = score
                best_id = livestock_id
                best_owner_name = owner_name

    if best_id and best_score >= soft_threshold:

        return {
            "duplicate": True,
            "existing_id": best_id,
            "similarity": float(best_score),
            "owner_name": best_owner_name,
            "confidence": get_confidence_label(float(best_score), threshold),
            "duplicate_type": "HARD" if best_score >= threshold else "SOFT_REVIEW"
        }

    return {
        "duplicate": False
    }


# ---------------------------------
# Global Verification (Authority)
# ---------------------------------

def verify_global_livestock(image_path, threshold=0.78):
    validation = validate_biometric_input(image_path)
    if not validation["valid"]:
        return {
            "status": "INVALID_INPUT",
            "similarity": 0.0,
            "confidence": "LOW",
            "reason": validation["reason"]
        }

    embedding = get_embedding_list(image_path)
    embedding = np.array(embedding, dtype=np.float32)

    results = search_embedding(embedding, k=5)

    if len(results) == 0:
        return {
            "status": "NOT_FOUND",
            "similarity": 0
        }

    candidate_ids = []
    for livestock_id, _ in results:
        if livestock_id not in candidate_ids:
            candidate_ids.append(livestock_id)

    best_id = None
    best_score = -1.0
    best_record = None

    for livestock_id in candidate_ids:
        record = get_livestock_by_id(livestock_id)
        if not record:
            continue
        for stored in _record_embeddings(record):
            score = cosine_similarity(embedding, stored)
            if score > best_score:
                best_score = score
                best_id = livestock_id
                best_record = record

    if best_id and best_score >= threshold:

        record = best_record
        owner_name = "Unknown"
        if record:
            if "owner_name" in record and record["owner_name"]:
                owner_name = record["owner_name"]
            elif "owner_id" in record and record["owner_id"]:
                farmer = get_farmer_by_id(record["owner_id"])
                if farmer and "username" in farmer:
                    owner_name = farmer["username"]

        return {
            "status": "FOUND",
            "livestock_id": best_id,
            "owner_name": owner_name,
            "similarity": float(best_score),
            "confidence": get_confidence_label(float(best_score), threshold)
        }

    return {
        "status": "NOT_FOUND",
        "similarity": float(best_score if best_score > -1 else 0.0),
        "confidence": get_confidence_label(float(best_score if best_score > -1 else 0.0), threshold)
    }

# ---------------------------------
# Farmer Scoped Verification
# ---------------------------------

def verify_farmer_livestock(image_path, owner_id, threshold=0.78):
    validation = validate_biometric_input(image_path)
    if not validation["valid"]:
        return {
            "status": "INVALID_INPUT",
            "similarity": 0.0,
            "confidence": "LOW",
            "reason": validation["reason"]
        }

    embedding = get_embedding_list(image_path)

    embedding = np.array(embedding, dtype=np.float32)

    records = get_farmer_livestock(owner_id)

    if len(records) == 0:
        return {
            "status": "NOT_FOUND",
            "similarity": 0.0,
            "confidence": "LOW"
        }

    best_match = None
    best_score = -1

    for r in records:
        livestock_id = r["livestock_id"]
        for stored in _record_embeddings(r):
            score = cosine_similarity(embedding, stored)
            if score > best_score:
                best_score = score
                best_match = livestock_id

    if best_score >= threshold:

        return {
            "status": "FOUND",
            "livestock_id": best_match,
            "similarity": float(best_score),
            "confidence": get_confidence_label(float(best_score), threshold)
        }

    return {
        "status": "NOT_FOUND",
        "similarity": float(best_score),
        "confidence": get_confidence_label(float(best_score), threshold)
    }
