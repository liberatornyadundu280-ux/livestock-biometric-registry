from pymongo.errors import PyMongoError

from core.database import delete_livestock_by_id, register_livestock
from core.vector_index import add_vector


def register_livestock_transaction(record):
    """
    Transaction-like registration flow:
    1) Insert into MongoDB
    2) Add embedding to FAISS
    If step 2 fails, rollback DB insert.
    """
    livestock_id = record["livestock_id"]
    embedding = record["embedding"]

    try:
        register_livestock(record)
    except PyMongoError as exc:
        return {
            "ok": False,
            "stage": "db_insert",
            "error": str(exc),
        }

    try:
        add_vector(embedding, livestock_id)
    except Exception as exc:  # FAISS errors are not PyMongoError
        delete_livestock_by_id(livestock_id)
        return {
            "ok": False,
            "stage": "faiss_add",
            "error": str(exc),
        }

    return {
        "ok": True,
        "livestock_id": livestock_id,
    }
