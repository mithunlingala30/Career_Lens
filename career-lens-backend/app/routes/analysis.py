from fastapi import APIRouter, Depends, HTTPException

from ..database import get_store
from ..schemas import ProfileUpdate
from ..services.resume_parser import parse_resume
from ..services.resume_service import make_profile, profile_to_dict
from ..utils.helpers import owned_resume
from ..utils.security import require_candidate

router = APIRouter(prefix="/api/analysis", tags=["Resume Analysis"])


def _save(store, resume, profile):
    store.put("candidate_profiles", profile)
    store.put("resumes", {**resume, "status": "extracted", "candidate_name": profile["full_name"]})
    return profile_to_dict(store.get("candidate_profiles", resume["id"]))


@router.post("/extract/{resume_id}")
def extract(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    resume = owned_resume(store, resume_id, user)
    parsed = parse_resume(resume["raw_text"])
    existing = store.get("candidate_profiles", resume_id)
    profile = make_profile(resume, parsed, parsed_years=parsed.get("total_experience_years", 0.0), existing={"created_at": existing["created_at"]} if existing else None)
    return _save(store, resume, profile)


@router.get("/{resume_id}")
def get_profile(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    owned_resume(store, resume_id, user)
    p = store.get("candidate_profiles", resume_id)
    if not p:
        raise HTTPException(404, "This resume has not been analysed yet")
    return profile_to_dict(p)


@router.put("/{resume_id}")
def update_profile(resume_id: int, body: ProfileUpdate, store=Depends(get_store), user: dict = Depends(require_candidate)):
    """Save user corrections to the extracted details (replaces all lists)."""
    resume = owned_resume(store, resume_id, user)
    old = store.get("candidate_profiles", resume_id)
    if not old:
        raise HTTPException(404, "This resume has not been analysed yet")
    weights = {s["skill_name"]: s["evidence_weight"] for s in old["skills"]}
    profile = make_profile(resume, body.model_dump(), old_weights=weights, edited=True, existing={"created_at": old["created_at"]})
    return _save(store, resume, profile)
