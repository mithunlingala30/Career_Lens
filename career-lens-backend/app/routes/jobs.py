from fastapi import APIRouter, Depends, HTTPException

from ..database import get_store
from ..schemas import ExtractSkillsIn, JobIn, RenameCategoryIn
from ..services.resume_parser import extract_job_skills
from ..services.skills_taxonomy import canonical
from ..utils.security import get_current_user, require_admin

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def _requirements(body: JobIn) -> list:
    reqs = [r.model_dump() for r in body.requirements] or extract_job_skills(body.description)
    seen, out = set(), []
    for r in reqs:
        name = canonical(r["skill_name"])
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({"skill_name": name, "importance": int(r["importance"]), "is_mandatory": bool(r.get("is_mandatory"))})
    if not out:
        raise HTTPException(422, "Add at least one required skill (none could be detected in the description)")
    return sorted(out, key=lambda r: -r["importance"])


def _clash(store, body, exclude_id=None):
    return any(j["title"].lower() == body.title.lower() and j.get("company", "").lower() == body.company.lower() and j["id"] != exclude_id
               for j in store.all("jobs"))


@router.get("")
def list_jobs(active_only: bool = False, q: str = "", category: str = "", store=Depends(get_store), _=Depends(get_current_user)):
    jobs = store.all("jobs")
    if active_only:
        jobs = [j for j in jobs if j.get("is_active", True)]
    if category:
        jobs = [j for j in jobs if j["category"] == category]
    if q:
        ql = q.lower()
        jobs = [j for j in jobs if ql in f"{j['title']} {j.get('company', '')} {j.get('description', '')}".lower()]
    return sorted(jobs, key=lambda j: -j["id"])


@router.get("/categories")
def categories(store=Depends(get_store), _=Depends(get_current_user)):
    counts = {}
    for j in store.all("jobs"):
        counts[j["category"]] = counts.get(j["category"], 0) + 1
    return [{"category": c, "jobs": n} for c, n in sorted(counts.items())]


@router.put("/categories/rename")
def rename_category(body: RenameCategoryIn, store=Depends(get_store), _=Depends(require_admin)):
    jobs = store.where("jobs", category=body.old)
    if not jobs:
        raise HTTPException(404, "Category not found")
    for j in jobs:
        store.update("jobs", j["id"], {"category": body.new.strip()})
    return {"updated_jobs": len(jobs)}


@router.post("/extract-skills")
def extract_skills(body: ExtractSkillsIn, _=Depends(require_admin)):
    return extract_job_skills(body.description)


@router.get("/{job_id}")
def get_job(job_id: int, store=Depends(get_store), _=Depends(get_current_user)):
    j = store.get("jobs", job_id)
    if not j:
        raise HTTPException(404, "Job not found")
    return j


@router.post("", status_code=201)
def create_job(body: JobIn, store=Depends(get_store), admin: dict = Depends(require_admin)):
    if _clash(store, body):
        raise HTTPException(409, "A job with this title and company already exists")
    return store.create("jobs", {**body.model_dump(exclude={"requirements"}), "requirements": _requirements(body), "created_by": admin["id"]})


@router.put("/{job_id}")
def update_job(job_id: int, body: JobIn, store=Depends(get_store), _=Depends(require_admin)):
    job = store.get("jobs", job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if _clash(store, body, job_id):
        raise HTTPException(409, "Another job with this title and company already exists")
    return store.update("jobs", job_id, {**body.model_dump(exclude={"requirements"}), "requirements": _requirements(body)})


@router.delete("/{job_id}")
def delete_job(job_id: int, store=Depends(get_store), _=Depends(require_admin)):
    if not store.get("jobs", job_id):
        raise HTTPException(404, "Job not found")
    for col in ("skill_gaps", "job_matches", "resume_evaluations"):
        store.delete_where(col, job_id=job_id)
    for h in store.where("evaluation_history", job_id=job_id):
        store.update("evaluation_history", h["id"], {"job_id": None, "evaluation_id": None})
    store.delete("jobs", job_id)
    return {"deleted": True}
