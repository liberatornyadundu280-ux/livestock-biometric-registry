from core.database import get_all_farmer_ids, get_all_livestock_ids

def generate_livestock_id():
    max_num = 0
    for livestock_id in get_all_livestock_ids():
        if not livestock_id.startswith("LS"):
            continue
        suffix = livestock_id[2:]
        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

    return f"LS{max_num + 1:04d}"


def generate_farmer_id():
    max_num = 0
    for farmer_id in get_all_farmer_ids():
        if not farmer_id.startswith("F"):
            continue
        suffix = farmer_id[1:]
        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

    return f"F{max_num + 1:04d}"
