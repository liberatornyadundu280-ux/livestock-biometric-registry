import importlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import numpy as np


def _reload_verifier_with_stubbed_embedding():
    """Avoid loading the heavy torch model during backend unit tests."""
    stub_module = types.SimpleNamespace(
        get_embedding_list=lambda _path: [0.0] * 1280
    )
    validator_stub = types.SimpleNamespace(
        validate_biometric_input=lambda _path: {"valid": True}
    )
    with patch.dict(sys.modules, {"core.embedding": stub_module}):
        with patch.dict(sys.modules, {"core.input_validator": validator_stub}):
            if "core.verifier" in sys.modules:
                del sys.modules["core.verifier"]
            return importlib.import_module("core.verifier")


class BackendStage1Tests(unittest.TestCase):
    def test_registration_writes_record(self):
        from core import database

        record = {
            "livestock_id": "LS9999",
            "owner_id": "F001",
            "owner_name": "farmer_a",
            "embedding": [0.1] * 1280,
        }

        with patch.object(database, "livestock_collection") as mock_collection:
            database.register_livestock(record)
            mock_collection.insert_one.assert_called_once_with(record)

    def test_duplicate_detection_works(self):
        verifier = _reload_verifier_with_stubbed_embedding()

        with patch.object(
            verifier,
            "search_embedding",
            return_value=[("LS0001", 0.93)],
        ), patch.object(
            verifier,
            "get_livestock_by_id",
            return_value={"owner_name": "farmer_one", "embedding": [0.2] * 1280},
        ):
            result = verifier.check_duplicate([0.2] * 1280, threshold=0.78)

        self.assertTrue(result["duplicate"])
        self.assertEqual(result["existing_id"], "LS0001")
        self.assertEqual(result["owner_name"], "farmer_one")
        self.assertGreaterEqual(result["similarity"], 0.78)

    def test_global_verification_returns_owner(self):
        verifier = _reload_verifier_with_stubbed_embedding()

        with patch.object(
            verifier,
            "get_embedding_list",
            return_value=[0.4] * 1280,
        ), patch.object(
            verifier,
            "search_embedding",
            return_value=[("LS0012", 0.88)],
        ), patch.object(
            verifier,
            "get_livestock_by_id",
            return_value={"owner_name": "farmer_two", "embedding": [0.4] * 1280},
        ):
            result = verifier.verify_global_livestock("dummy.jpg", threshold=0.78)

        self.assertEqual(result["status"], "FOUND")
        self.assertEqual(result["livestock_id"], "LS0012")
        self.assertEqual(result["owner_name"], "farmer_two")
        self.assertGreaterEqual(result["similarity"], 0.78)

    def test_global_verification_handles_missing_owner_name(self):
        verifier = _reload_verifier_with_stubbed_embedding()

        with patch.object(
            verifier,
            "get_embedding_list",
            return_value=[0.4] * 1280,
        ), patch.object(
            verifier,
            "search_embedding",
            return_value=[("LS0099", 0.86)],
        ), patch.object(
            verifier,
            "get_livestock_by_id",
            return_value={"owner_id": "F0042", "embedding": [0.4] * 1280},
        ), patch.object(
            verifier,
            "get_farmer_by_id",
            return_value={"username": "fallback_farmer"},
        ):
            result = verifier.verify_global_livestock("dummy.jpg", threshold=0.78)

        self.assertEqual(result["status"], "FOUND")
        self.assertEqual(result["livestock_id"], "LS0099")
        self.assertEqual(result["owner_name"], "fallback_farmer")
        self.assertGreaterEqual(result["similarity"], 0.78)

    def test_faiss_index_updates_after_add(self):
        from core import vector_index
        import faiss

        original_index = vector_index.index
        original_id_map = list(vector_index.id_map)
        try:
            vector_index.index = faiss.IndexFlatIP(vector_index.DIMENSION)
            vector_index.id_map = []

            raw = np.random.default_rng(7).random(vector_index.DIMENSION).astype(
                np.float32
            )
            norm = np.linalg.norm(raw)
            embedding = (raw / norm).astype(np.float32)

            vector_index.add_vector(embedding.tolist(), "LSTEST")
            result = vector_index.search_embedding(embedding.tolist(), k=1)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], "LSTEST")
            self.assertGreaterEqual(result[0][1], 0.99)
        finally:
            vector_index.index = original_index
            vector_index.id_map = original_id_map


if __name__ == "__main__":
    unittest.main()
