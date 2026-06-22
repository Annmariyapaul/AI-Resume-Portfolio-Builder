"""utils/validators.py — Simple request validation helpers."""


def validate_required_fields(data: dict, fields: list[str]) -> str | None:
    """
    Check that all *fields* exist and are non-empty in *data*.
    Returns an error message string on failure, or None on success.
    """
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    return None
