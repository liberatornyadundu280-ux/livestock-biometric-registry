import os


DEFAULT_MATCH_THRESHOLD = 0.78
MIN_THRESHOLD = 0.30
MAX_THRESHOLD = 0.95


def _parse_threshold(raw_value):
    try:
        value = float(str(raw_value).strip())
    except (TypeError, ValueError):
        return None

    if value < MIN_THRESHOLD:
        return MIN_THRESHOLD
    if value > MAX_THRESHOLD:
        return MAX_THRESHOLD
    return value


def get_match_threshold():
    """
    Centralized match threshold source.
    Priority:
    1) BIO_MATCH_THRESHOLD env var
    2) local THRESHOLD file (if present)
    3) DEFAULT_MATCH_THRESHOLD
    """
    env_value = _parse_threshold(os.getenv("BIO_MATCH_THRESHOLD"))
    if env_value is not None:
        return env_value

    threshold_file = os.path.join(os.getcwd(), "THRESHOLD")
    if os.path.exists(threshold_file):
        with open(threshold_file, "r", encoding="utf-8") as f:
            file_value = _parse_threshold(f.read())
            if file_value is not None:
                return file_value

    return DEFAULT_MATCH_THRESHOLD
