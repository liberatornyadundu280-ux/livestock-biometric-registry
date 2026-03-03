import torch
import torch.nn.functional as F
from database.db_handler import get_all_livestock


# -------------------------------------------------
# Verification Function (Farmer Side)
# -------------------------------------------------
def verify_livestock(image_path, threshold, owner_id):
    from core.embedding import get_embedding
    from database.db_handler import get_livestock_by_owner

    input_embedding = get_embedding(image_path)

    livestock_records = get_livestock_by_owner(owner_id)

    best_match = None
    highest_similarity = 0

    for record in livestock_records:
        stored_embedding = torch.tensor(record["embedding"]).unsqueeze(0)
        similarity = F.cosine_similarity(input_embedding, stored_embedding).item()

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = record

    if best_match and highest_similarity >= threshold:
        return {
            "status": "VERIFIED",
            "similarity": highest_similarity,
            "livestock_id": best_match["livestock_id"],
            "owner_name": best_match["owner_name"]
        }

    return {
        "status": "NOT_VERIFIED",
        "similarity": highest_similarity
    }
# -------------------------------------------------
# Duplicate Check (Authority Side)
# -------------------------------------------------
def check_duplicate(embedding, threshold=0.85):
    livestock_records = get_all_livestock()

    best_match = None
    highest_similarity = 0

    input_embedding = torch.tensor(embedding).unsqueeze(0)

    for record in livestock_records:
        stored_embedding = torch.tensor(record["embedding"]).unsqueeze(0)
        similarity = F.cosine_similarity(input_embedding, stored_embedding).item()

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = record

    if best_match and highest_similarity >= threshold:
        return {
            "duplicate": True,
            "similarity": highest_similarity,
            "existing_id": best_match["livestock_id"],
            "owner_name": best_match["owner_name"]
        }

    return {
        "duplicate": False
    }

def verify_global_livestock(image_path, threshold):
    from core.embedding import get_embedding
    from database.db_handler import get_all_livestock

    input_embedding = get_embedding(image_path)

    livestock_records = get_all_livestock()

    best_match = None
    highest_similarity = 0

    for record in livestock_records:
        stored_embedding = torch.tensor(record["embedding"]).unsqueeze(0)
        similarity = F.cosine_similarity(input_embedding, stored_embedding).item()

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = record

    if best_match and highest_similarity >= threshold:
        return {
            "status": "FOUND",
            "similarity": highest_similarity,
            "livestock_id": best_match["livestock_id"],
            "owner_name": best_match["owner_name"]
        }

    return {
        "status": "NOT_FOUND",
        "similarity": highest_similarity
    }