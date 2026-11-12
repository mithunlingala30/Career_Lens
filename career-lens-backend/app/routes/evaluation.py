from fastapi import APIRouter, Depends, HTTPException

from ..database import get_store
from ..services import reference
from ..services.analysis_service import run_single_evaluation
from ..utils.helpers import newest_first, owned_resume
from ..utils.security import require_candidate

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])


def eval_to_dict(e: dict) -> dict:
    return {**e["details"], "id": e["id"], "resume_id": e["resume_id"], "job_id": e["job_id"], "evaluated_at": e["updated_at"]}


@router.get("/history")
def history(store=Depends(get_store), user: dict = Depends(require_candidate)):
    rows = newest_first(store.where("evaluation_history", user_id=user["id"]))[:300]
    return [{k: h.get(k) for k in ("id", "event_type", "title", "resume_id", "resume_name", "evaluation_id", "job_id", "scores", "created_at")} for h in rows]


@router.get("/validation")
def validation(_: dict = Depends(require_candidate)):
    """Hypothesis-test result: proposed matching algorithm vs keyword baseline."""
    return reference.get_reference()["hypothesis"]


@router.post("/{resume_id}/{job_id}")
def evaluate(resume_id: int, job_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    return eval_to_dict(run_single_evaluation(owned_resume(store, resume_id, user), job_id))


@router.get("/{resume_id}")
def get_evaluations(resume_id: int, job_id: int = None, store=Depends(get_store), user: dict = Depends(require_candidate)):
    owned_resume(store, resume_id, user)
    q = {"resume_id": resume_id, **({"job_id": job_id} if job_id is not None else {})}
    rows = store.where("resume_evaluations", **q)
    if job_id is not None:
        if not rows:
            raise HTTPException(404, "No evaluation for this job yet")
        return eval_to_dict(rows[0])
    rows.sort(key=lambda e: -e["compatibility"])
    return [{"id": e["id"], "job_id": e["job_id"], "job_title": e["details"].get("job_title"), "company": e["details"].get("company"),
             "compatibility": e["compatibility"], "resume_score": e["resume_score"], "updated_at": e["updated_at"]} for e in rows]
