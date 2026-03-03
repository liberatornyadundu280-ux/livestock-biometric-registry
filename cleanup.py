from database.db_handler import load_database, save_database

db = load_database()

# Remove all livestock
db["livestock"] = []

# Reset farmer livestock IDs
for farmer in db["farmers"]:
    farmer["livestock_ids"] = []

save_database(db)

print("Database cleaned successfully.")