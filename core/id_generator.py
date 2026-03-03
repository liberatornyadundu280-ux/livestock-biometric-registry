from database.db_handler import load_database

def generate_livestock_id():
    db = load_database()
    count = len(db["livestock"]) + 1
    return f"LS{count:04d}"