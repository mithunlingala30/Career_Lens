import numpy as np
from fastapi import HTTPException


def to_native(obj):
    """Recursively convert numpy / non-JSON types to plain Python so documents can be stored."""
    if isinstance(obj, dict):
        return {str(k): to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_native(v) for v in obj]
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, float) and (obj != obj or obj in (float("inf"), float("-inf"))):
        return 0.0
    return obj


def owned_resume(store, resume_id: int, user: dict) -> dict:
    r = store.get("resumes", resume_id)
    if not r or r["user_id"] != user["id"]:
        raise HTTPException(404, "Resume not found")
    return r


def user_out(u: dict) -> dict:
    return {"id": u["id"], "full_name": u["full_name"], "email": u["email"], "role": u["role"], "created_at": u.get("created_at")}


def newest_first(docs):
    return sorted(docs, key=lambda d: (d.get("created_at", ""), d["id"]), reverse=True)
