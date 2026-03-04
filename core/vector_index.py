import faiss
import numpy as np

from core.database import get_all_livestock_embeddings

# ---------------------------------
# Embedding dimension
# ---------------------------------

DIMENSION = 1280

# ---------------------------------
# FAISS index (cosine similarity)
# ---------------------------------

index = faiss.IndexFlatIP(DIMENSION)

# map FAISS position -> livestock_id
id_map = []


# ---------------------------------
# Build index from database
# ---------------------------------

def build_index():

    global index
    global id_map

    # Recreate index to avoid duplicate vectors on rebuild.
    index = faiss.IndexFlatIP(DIMENSION)

    records = get_all_livestock_embeddings()

    vectors = []
    id_map = []

    for livestock_id, embedding in records:

        vectors.append(embedding)
        id_map.append(livestock_id)

    if len(vectors) == 0:
        print("No livestock embeddings found.")
        return

    vectors = np.array(vectors, dtype=np.float32)
    faiss.normalize_L2(vectors)

    index.add(vectors)

    print(f"FAISS index built with {len(vectors)} livestock embeddings.")


# ---------------------------------
# Search FAISS index
# ---------------------------------

def search_embedding(query_embedding, k=1):

    query = np.array([query_embedding], dtype=np.float32)
    faiss.normalize_L2(query)

    distances, indices = index.search(query, k)

    results = []

    for i in range(k):

        idx = indices[0][i]

        if idx == -1:
            continue

        livestock_id = id_map[idx]
        score = distances[0][i]

        results.append((livestock_id, score))

    return results
def add_vector(embedding, livestock_id):
    """
    Add a new embedding to the FAISS index
    """

    global index
    global id_map

    vector = np.array([embedding], dtype=np.float32)
    faiss.normalize_L2(vector)

    index.add(vector)

    id_map.append(livestock_id)


def add_vectors(embeddings, livestock_ids):
    """
    Batch add embeddings to FAISS index.
    """
    if not embeddings:
        return 0

    vectors = np.array(embeddings, dtype=np.float32)
    faiss.normalize_L2(vectors)
    index.add(vectors)
    id_map.extend(livestock_ids)
    return len(livestock_ids)


def get_index_size():
    """
    Number of vectors currently loaded in FAISS in-memory index.
    """
    return len(id_map)
