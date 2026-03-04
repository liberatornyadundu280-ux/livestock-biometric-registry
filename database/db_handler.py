import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.json")


def load_database():
    if not os.path.exists(DB_PATH):
        return {"farmers": [], "livestock": []}

    with open(DB_PATH, "r") as file:
        return json.load(file)


def save_database(data):
    with open(DB_PATH, "w") as file:
        json.dump(data, file, indent=4)


# =============================
# Farmer Functions
# =============================

def get_farmer_by_username(username):
    db = load_database()
    for farmer in db["farmers"]:
        if farmer["username"] == username:
            return farmer
    return None


def get_farmer_by_id(farmer_id):
    db = load_database()
    for farmer in db["farmers"]:
        if farmer["farmer_id"] == farmer_id:
            return farmer
    return None


# =============================
# Livestock Functions
# =============================

def add_livestock_record(livestock_record):
    db = load_database()
    db["livestock"].append(livestock_record)

    # Update farmer livestock list
    for farmer in db["farmers"]:
        if farmer["farmer_id"] == livestock_record["owner_id"]:
            farmer["livestock_ids"].append(livestock_record["livestock_id"])
            break

    save_database(db)


def get_all_livestock():
    db = load_database()
    return db["livestock"]


def get_livestock_by_owner(owner_id):
    db = load_database()
    return [ls for ls in db["livestock"] if ls["owner_id"] == owner_id]

def get_livestock_by_id(livestock_id):
    """
    Retrieve a livestock record by ID
    """

    record = livestock_collection.find_one({"livestock_id": livestock_id})

    return record