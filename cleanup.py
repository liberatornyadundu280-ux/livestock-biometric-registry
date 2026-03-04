import argparse

from core.database import (
    count_farmers,
    count_livestock,
    farmers_collection,
    reset_livestock_registry,
)
from core.vector_index import build_index, get_index_size


def main():
    parser = argparse.ArgumentParser(description="Cleanup MongoDB registry data.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Also remove farmers (default only removes livestock).",
    )
    args = parser.parse_args()

    before_livestock = count_livestock()
    before_farmers = count_farmers()

    removed_livestock = reset_livestock_registry()

    removed_farmers = 0
    if args.all:
        removed_farmers = farmers_collection.delete_many({}).deleted_count

    # Rebuild in-memory FAISS for this process to reflect cleanup.
    build_index()

    print("Cleanup complete.")
    print(f"Removed livestock records: {removed_livestock}")
    print(f"Removed farmer records: {removed_farmers}")
    print(f"Before -> livestock: {before_livestock}, farmers: {before_farmers}")
    print(f"After  -> livestock: {count_livestock()}, farmers: {count_farmers()}")
    print(f"FAISS vectors in this process: {get_index_size()}")


if __name__ == "__main__":
    main()
