from collections import Counter

from core import database
from core.vector_index import build_index, get_index_size


def _db_vector_count():
    count = 0
    for record in database.livestock_collection.find({}, {"embedding": 1, "embedding_gallery": 1}):
        if "embedding_gallery" in record and isinstance(record["embedding_gallery"], list):
            count += len(record["embedding_gallery"])
        elif "embedding" in record and isinstance(record["embedding"], list):
            count += 1
    return count


def generate_registry_report():
    """
    Snapshot registry consistency between MongoDB and FAISS in-memory index.
    """
    records = list(
        database.livestock_collection.find(
            {},
            {"_id": 0, "livestock_id": 1, "embedding": 1, "embedding_gallery": 1},
        )
    )
    livestock_ids = [r.get("livestock_id") for r in records if r.get("livestock_id")]
    id_counts = Counter(livestock_ids)
    duplicate_ids = sorted([lid for lid, n in id_counts.items() if n > 1])

    records_without_embeddings = 0
    for r in records:
        has_gallery = "embedding_gallery" in r and isinstance(r["embedding_gallery"], list) and len(r["embedding_gallery"]) > 0
        has_single = "embedding" in r and isinstance(r["embedding"], list) and len(r["embedding"]) > 0
        if not has_gallery and not has_single:
            records_without_embeddings += 1

    db_records = len(records)
    db_vectors = _db_vector_count()
    faiss_vectors = get_index_size()

    return {
        "db_records": db_records,
        "db_embedding_vectors": db_vectors,
        "db_vectors": db_vectors,
        "faiss_embedding_vectors": faiss_vectors,
        "faiss_vectors": faiss_vectors,
        "count_mismatch": db_vectors != faiss_vectors,
        "duplicate_livestock_ids": duplicate_ids,
        "records_without_embeddings": records_without_embeddings,
    }


def reconcile_registry():
    """
    Rebuild FAISS from MongoDB and return before/after reports.
    """
    before = generate_registry_report()
    build_index()
    after = generate_registry_report()
    return {
        "before": before,
        "after": after,
        "repaired": before["count_mismatch"] and not after["count_mismatch"],
    }
