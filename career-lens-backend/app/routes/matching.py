from fastapi import APIRouter, Depends

from ..database import get_store
from ..services.analysis_service import run_matching
from ..utils.helpers import owned_resume
from ..utils.security import require_candidate

router = APIRouter(prefix="/api/matching", tags=["Job Matching"])


def _payload(store, resume_id):
    rows = sorted(store.where("job_matches", resume_id=resume_id), key=lambda m: m["rank"])
    jobs = {j["id"]: j for j in store.all("jobs")}
    return {"resume_id": resume_id, "generated_at": rows[0]["updated_at"] if rows else None,
            "matches": [{"rank": m["rank"], "compatibility": m["compatibility"], "matched_count": m["matched_count"],
                         "missing_count": m["missing_count"], "job": jobs[m["job_id"]], **m["details"]} for m in rows if m["job_id"] in jobs]}


@router.post("/{resume_id}")
def run(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    run_matching(owned_resume(store, resume_id, user))
    return _payload(store, resume_id)


@router.get("/{resume_id}")
def get(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    owned_resume(store, resume_id, user)
    return _payload(store, resume_id)
