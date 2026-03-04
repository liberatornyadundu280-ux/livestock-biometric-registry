import os
import unittest
from unittest.mock import patch

import faiss
import numpy as np
from pymongo import MongoClient

from core import database, registry_service, vector_index
from core.reconciliation import generate_registry_report, reconcile_registry


class Stage1IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1500)
        try:
            cls.client.admin.command("ping")
        except Exception as exc:
            raise unittest.SkipTest(f"MongoDB not available for integration tests: {exc}")

        cls.original_farmers_collection = database.farmers_collection
        cls.original_livestock_collection = database.livestock_collection

        cls.test_db_name = f"livestock_registry_it_{os.getpid()}"
        cls.test_db = cls.client[cls.test_db_name]
        database.farmers_collection = cls.test_db["farmers"]
        database.livestock_collection = cls.test_db["livestock"]
        database.ensure_indexes()

    @classmethod
    def tearDownClass(cls):
        database.farmers_collection = cls.original_farmers_collection
        database.livestock_collection = cls.original_livestock_collection
        cls.client.drop_database(cls.test_db_name)

    def setUp(self):
        database.farmers_collection.delete_many({})
        database.livestock_collection.delete_many({})
        database.ensure_indexes()
        vector_index.index = faiss.IndexFlatIP(vector_index.DIMENSION)
        vector_index.id_map = []

    def _random_embedding(self, seed):
        rng = np.random.default_rng(seed)
        vec = rng.random(vector_index.DIMENSION).astype(np.float32)
        vec /= np.linalg.norm(vec) + 1e-12
        return vec.tolist()

    def test_register_transaction_writes_db_and_faiss(self):
        emb = self._random_embedding(1)
        record = {
            "livestock_id": "LS9001",
            "livestock_type": "cattle",
            "biometric_type": "muzzle",
            "owner_id": "F9001",
            "owner_name": "farmer_it",
            "embedding": emb,
            "embedding_gallery": [emb],
        }

        result = registry_service.register_livestock_transaction(record)
        self.assertTrue(result["ok"])
        self.assertEqual(database.count_livestock(), 1)
        self.assertEqual(vector_index.get_index_size(), 1)

    def test_append_gallery_reflects_in_rebuild(self):
        emb1 = self._random_embedding(2)
        emb2 = self._random_embedding(3)
        database.register_livestock(
            {
                "livestock_id": "LS9002",
                "livestock_type": "cattle",
                "biometric_type": "muzzle",
                "owner_id": "F9001",
                "owner_name": "farmer_it",
                "embedding": emb1,
                "embedding_gallery": [emb1],
            }
        )
        ok = database.append_livestock_embedding("LS9002", emb2)
        self.assertTrue(ok)

        vector_index.build_index()
        self.assertEqual(vector_index.get_index_size(), 2)
        self.assertEqual(vector_index.id_map.count("LS9002"), 2)

    def test_transaction_rolls_back_on_faiss_failure(self):
        emb = self._random_embedding(4)
        record = {
            "livestock_id": "LS9003",
            "livestock_type": "cattle",
            "biometric_type": "muzzle",
            "owner_id": "F9001",
            "owner_name": "farmer_it",
            "embedding": emb,
            "embedding_gallery": [emb],
        }

        with patch("core.registry_service.add_vector", side_effect=RuntimeError("faiss down")):
            result = registry_service.register_livestock_transaction(record)

        self.assertFalse(result["ok"])
        self.assertEqual(result["stage"], "faiss_add")
        self.assertEqual(database.count_livestock(), 0)

    def test_reconciliation_repairs_faiss_count_mismatch(self):
        emb = self._random_embedding(5)
        database.register_livestock(
            {
                "livestock_id": "LS9004",
                "livestock_type": "cattle",
                "biometric_type": "muzzle",
                "owner_id": "F9001",
                "owner_name": "farmer_it",
                "embedding": emb,
                "embedding_gallery": [emb],
            }
        )
        # Intentionally do not add to FAISS to create mismatch.
        report_before = generate_registry_report()
        self.assertTrue(report_before["count_mismatch"])

        result = reconcile_registry()
        self.assertFalse(result["after"]["count_mismatch"])


if __name__ == "__main__":
    unittest.main()
