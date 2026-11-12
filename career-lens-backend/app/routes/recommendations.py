from fastapi import APIRouter, Depends

from ..database import get_store
from ..services.analysis_service import run_recommendations
from ..utils.helpers import owned_resume
from ..utils.security import require_candidate

router = APIRouter(prefix="/api/recommendations", tags=["Career Recommendations"])


def _payload(store, resume_id):
    rows = sorted(store.where("career_recommendations", resume_id=resume_id), key=lambda r: r["rank"])
    return {"resume_id": resume_id, "recommendations": rows}


@router.post("/{resume_id}")
def run(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    run_recommendations(owned_resume(store, resume_id, user))
    return _payload(store, resume_id)


@router.get("/{resume_id}")
def get(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    owned_resume(store, resume_id, user)
    return _payload(store, resume_id)
