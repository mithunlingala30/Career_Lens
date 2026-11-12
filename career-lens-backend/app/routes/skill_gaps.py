from fastapi import APIRouter, Depends

from ..database import get_store
from ..services.skills_taxonomy import AREA_TIPS, area_of
from ..utils.helpers import owned_resume
from ..utils.security import require_candidate

router = APIRouter(prefix="/api/skill-gaps", tags=["Skill Gap Analysis"])


@router.get("/{resume_id}")
def skill_gaps(resume_id: int, job_id: int = None, store=Depends(get_store), user: dict = Depends(require_candidate)):
    owned_resume(store, resume_id, user)
    matches = sorted(store.where("job_matches", resume_id=resume_id), key=lambda m: m["rank"])
    jobs = {j["id"]: j for j in store.all("jobs")}
    gaps = {g["job_id"]: g for g in store.where("skill_gaps", resume_id=resume_id)}
    selected = job_id if job_id in gaps else (matches[0]["job_id"] if matches else None)
    sel = gaps.get(selected, {"matched": [], "missing": []})
    missing = [{**m, "area": area_of(m["skill"])} for m in sel["missing"]]
    agg = {}
    for g in gaps.values():
        for m in g["missing"]:
            a = agg.setdefault(m["skill"], {"skill": m["skill"], "jobs_requiring": 0, "importance": 0, "area": area_of(m["skill"])})
            a["jobs_requiring"] += 1
            a["importance"] += m["importance"]
    areas = {}
    for m in missing:
        areas.setdefault(m["area"], []).append(m["skill"])
    total_w = sum(x["importance"] for x in sel["matched"] + sel["missing"]) or 1
    profile = store.get("candidate_profiles", resume_id) or {"skills": []}
    return {
        "resume_id": resume_id, "selected_job_id": selected,
        "jobs": [{"id": m["job_id"], "title": jobs[m["job_id"]]["title"], "company": jobs[m["job_id"]].get("company", ""), "compatibility": m["compatibility"],
                  "matched": m["matched_count"], "missing": m["missing_count"]} for m in matches if m["job_id"] in jobs],
        "matched": sel["matched"], "missing": sorted(missing, key=lambda m: -m["importance"]),
        "coverage": round(100 * sum(x["importance"] for x in sel["matched"]) / total_w, 1),
        "candidate_skills": [{"skill": s["skill_name"], "type": s["skill_type"], "area": area_of(s["skill_name"]), "weight": s["evidence_weight"]} for s in profile["skills"]],
        "aggregate_missing": sorted(agg.values(), key=lambda a: (-a["jobs_requiring"], -a["importance"]))[:12],
        "learning_areas": [{"area": a, "skills": s, "tip": AREA_TIPS.get(a, "build a portfolio project")} for a, s in areas.items()],
    }
