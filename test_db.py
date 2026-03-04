from core.database import register_livestock, get_all_livestock_embeddings
import numpy as np

# ----------------------------------
# Create a dummy embedding
# ----------------------------------

embedding = np.random.rand(1280)

livestock_record = {
    "livestock_id": "TEST001",
    "owner_id": "F001",
    "livestock_type": "cattle",
    "biometric_type": "muzzle",
    "embedding": embedding.tolist()
}

# ----------------------------------
# Insert record into MongoDB
# ----------------------------------

print("Registering livestock...")

register_livestock(livestock_record)

print("Livestock inserted successfully.\n")

# ----------------------------------
# Retrieve embeddings
# ----------------------------------

print("Retrieving stored embeddings...")

records = get_all_livestock_embeddings()

for livestock_id, embedding in records:
    print("Livestock ID:", livestock_id)
    print("Embedding length:", len(embedding))
    print()

print("Database test complete.")