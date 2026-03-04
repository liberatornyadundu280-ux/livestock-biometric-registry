
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import numpy as np
from itertools import combinations
from core.embedding import get_embedding

DATASET_PATH = "dataset_raw/300_cattle_face"

THRESHOLD = 0.781

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2)

def load_embeddings():
    embeddings = {}

    for identity in os.listdir(DATASET_PATH):
        identity_path = os.path.join(DATASET_PATH, identity)

        if not os.path.isdir(identity_path):
            continue

        embeddings[identity] = []

        for img in os.listdir(identity_path):
            img_path = os.path.join(identity_path, img)
            emb = get_embedding(img_path)
            embeddings[identity].append(emb)

    return embeddings

def evaluate(embeddings):
    genuine_scores = []
    impostor_scores = []

    identities = list(embeddings.keys())

    # Genuine comparisons
    for identity in identities:
        embs = embeddings[identity]
        for emb1, emb2 in combinations(embs, 2):
            score = cosine_similarity(emb1, emb2)
            genuine_scores.append(score)

    # Impostor comparisons (sampled)
    for i in range(len(identities)):
        for j in range(i + 1, len(identities)):
            emb1 = random.choice(embeddings[identities[i]])
            emb2 = random.choice(embeddings[identities[j]])
            score = cosine_similarity(emb1, emb2)
            impostor_scores.append(score)

    return genuine_scores, impostor_scores

def compute_metrics(genuine_scores, impostor_scores):
    TP = sum(score >= THRESHOLD for score in genuine_scores)
    FN = sum(score < THRESHOLD for score in genuine_scores)

    FP = sum(score >= THRESHOLD for score in impostor_scores)
    TN = sum(score < THRESHOLD for score in impostor_scores)

    FAR = FP / (FP + TN)
    FRR = FN / (FN + TP)
    accuracy = (TP + TN) / (TP + TN + FP + FN)

    print("\n--- Evaluation Results ---")
    print(f"Threshold: {THRESHOLD}")
    print(f"Genuine Comparisons: {len(genuine_scores)}")
    print(f"Impostor Comparisons: {len(impostor_scores)}")
    print(f"FAR: {FAR:.4f}")
    print(f"FRR: {FRR:.4f}")
    print(f"Accuracy: {accuracy:.4f}")

if __name__ == "__main__":
    print("Loading embeddings...")
    embeddings = load_embeddings()

    print("Evaluating...")
    genuine_scores, impostor_scores = evaluate(embeddings)
    np.save("genuine_scores.npy", np.array(genuine_scores))
    np.save("impostor_scores.npy", np.array(impostor_scores))
    compute_metrics(genuine_scores, impostor_scores)