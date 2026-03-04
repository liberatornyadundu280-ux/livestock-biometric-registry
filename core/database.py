from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

# -----------------------------
# Database Connection
# -----------------------------

client = MongoClient("mongodb://localhost:27017/")

db = client["livestock_registry"]

farmers_collection = db["farmers"]
livestock_collection = db["livestock"]


def ping_database():
    """
    Check MongoDB connectivity.
    """
    try:
        client.admin.command("ping")
        return True, "MongoDB reachable"
    except Exception as exc:
        return False, str(exc)


def ensure_indexes():
    """
    Ensure required MongoDB indexes for integrity and query performance.
    """
    try:
        livestock_collection.create_index(
            [("livestock_id", ASCENDING)],
            unique=True,
            name="uniq_livestock_id",
        )
        livestock_collection.create_index(
            [("owner_id", ASCENDING)],
            name="idx_owner_id",
        )
        farmers_collection.create_index(
            [("farmer_id", ASCENDING)],
            unique=True,
            name="uniq_farmer_id",
        )
        farmers_collection.create_index(
            [("username", ASCENDING)],
            unique=True,
            name="uniq_farmer_username",
        )
        return True, "Indexes ready"
    except PyMongoError as exc:
        return False, str(exc)


# -----------------------------
# Farmer Operations
# -----------------------------

def register_farmer(farmer_data):
    """
    Insert a new farmer into the database
    """
    farmers_collection.insert_one(farmer_data)


def get_farmer(username):
    """
    Retrieve a farmer by username
    """
    return farmers_collection.find_one({"username": username})


def get_farmer_by_id(farmer_id):
    """
    Retrieve a farmer by farmer_id
    """
    return farmers_collection.find_one({"farmer_id": farmer_id})


def get_all_farmers():
    """
    Retrieve all farmer records
    """
    return list(farmers_collection.find({}))


def get_all_farmer_ids():
    """
    Retrieve all farmer IDs
    """
    return [
        record["farmer_id"]
        for record in farmers_collection.find({}, {"farmer_id": 1, "_id": 0})
    ]


def count_farmers():
    """
    Count farmer records.
    """
    return farmers_collection.count_documents({})


# -----------------------------
# Livestock Operations
# -----------------------------

def register_livestock(livestock_data):
    """
    Insert livestock record into database
    """
    livestock_collection.insert_one(livestock_data)


def delete_livestock_by_id(livestock_id):
    """
    Delete livestock record by ID.
    """
    result = livestock_collection.delete_one({"livestock_id": livestock_id})
    return result.deleted_count


def append_livestock_embedding(livestock_id, embedding):
    """
    Append a new view embedding to an existing livestock record.
    Supports legacy records with only 'embedding' field.
    """
    record = get_livestock_by_id(livestock_id)
    if not record:
        return False

    gallery = []
    if "embedding_gallery" in record and isinstance(record["embedding_gallery"], list):
        gallery = list(record["embedding_gallery"])
    elif "embedding" in record and isinstance(record["embedding"], list):
        gallery = [record["embedding"]]

    gallery.append(embedding)

    livestock_collection.update_one(
        {"livestock_id": livestock_id},
        {"$set": {"embedding_gallery": gallery}}
    )
    return True


def get_all_livestock_embeddings():
    """
    Retrieve all livestock embeddings for FAISS indexing
    """
    records = livestock_collection.find({})

    embeddings = []

    for r in records:
        livestock_id = r["livestock_id"]
        gallery = []
        if "embedding_gallery" in r and isinstance(r["embedding_gallery"], list):
            gallery = r["embedding_gallery"]
        elif "embedding" in r and isinstance(r["embedding"], list):
            gallery = [r["embedding"]]

        for emb in gallery:
            embeddings.append((livestock_id, emb))

    return embeddings


def get_farmer_livestock(owner_id):
    """
    Retrieve livestock owned by a specific farmer
    """
    records = livestock_collection.find({"owner_id": owner_id})

    livestock = []

    for r in records:
        livestock.append(r)

    return livestock


def get_livestock_by_id(livestock_id):
    """
    Retrieve a livestock record using its ID
    """
    record = livestock_collection.find_one({"livestock_id": livestock_id})

    return record


def get_all_livestock_ids():
    """
    Retrieve all livestock IDs
    """
    return [
        record["livestock_id"]
        for record in livestock_collection.find({}, {"livestock_id": 1, "_id": 0})
    ]


def count_livestock():
    """
    Count livestock records.
    """
    return livestock_collection.count_documents({})


def reset_livestock_registry():
    """
    Remove all livestock records for demo reset.
    """
    return livestock_collection.delete_many({}).deleted_count
