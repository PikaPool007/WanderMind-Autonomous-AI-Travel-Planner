def _extract_recos(obj):
    if obj is None:
        return []
    # pydantic model / object with attribute
    if hasattr(obj, "recommendations"):
        recos = getattr(obj, "recommendations", None)
        return recos or []
    # dict-shaped
    if isinstance(obj, dict):
        recos = obj.get("recommendations")
        return recos or []
    return []