from collections import Counter

from fastapi import APIRouter, Depends

from ..database import get_store
from ..services import reference
from ..services.skills_taxonomy import area_of
from ..utils.helpers import newest_first
from ..utils.security import require_admin, require_candidate

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/candidate")
def candidate_dashboard(store=Depends(get_store), user: dict = Depends(require_candidate)):
    resumes = newest_first(store.where("resumes", user_id=user["id"]))
    scores = [r["resume_score"] for r in resumes if r.get("resume_score") is not None]
    latest = next((r for r in resumes if r.get("resume_score") is not None), resumes[0] if resumes else None)
    matches, recs, gaps, profile = [], [], [], None
    if latest:
        matches = sorted(store.where("job_matches", resume_id=latest["id"]), key=lambda m: m["rank"])
        recs = sorted(store.where("career_recommendations", resume_id=latest["id"]), key=lambda r: r["rank"])
        gaps = store.where("skill_gaps", resume_id=latest["id"])
        profile = store.get("candidate_profiles", latest["id"])
    jobs = {j["id"]: j for j in store.all("jobs")} if matches else {}
    agg = {}
    for g in gaps:
        for m in g["missing"]:
            a = agg.setdefault(m["skill"], {"skill": m["skill"], "jobs_requiring": 0, "importance": 0})
            a["jobs_requiring"] += 1
            a["importance"] += m["importance"]
    hist = newest_first(store.where("evaluation_history", user_id=user["id"]))
    trend = [{"date": h["created_at"][5:16].replace("T", " "), "resume_score": h["scores"].get("resume_score"),
              "compatibility": h["scores"].get("top_compatibility", h["scores"].get("compatibility"))}
             for h in reversed(hist) if h["event_type"] in ("matching", "evaluation") and h["scores"].get("resume_score") is not None][-10:]
    areas = Counter(area_of(s["skill_name"]) for s in (profile["skills"] if profile else []))
    top = matches[0] if matches and matches[0]["job_id"] in jobs else None
    return {
        "stats": {"resumes": len(resumes), "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
                  "matching_jobs": sum(1 for m in matches if m["compatibility"] >= 50), "readiness": recs[0]["readiness"] if recs else 0,
                  "top_job": {"title": jobs[top["job_id"]]["title"], "compatibility": top["compatibility"]} if top else None},
        "latest_resume": {"id": latest["id"], "name": latest["original_filename"], "analysed": latest["status"] == "extracted"} if latest else None,
        "recent": [{"id": h["id"], "event_type": h["event_type"], "title": h["title"], "scores": h["scores"], "created_at": h["created_at"],
                    "resume_id": h.get("resume_id"), "job_id": h.get("job_id")} for h in hist[:6]],
        "recommended_roles": [{"category": r["category"], "suitability": r["suitability"], "readiness": r["readiness"]} for r in recs[:4]],
        "skill_gap_summary": sorted(agg.values(), key=lambda a: (-a["jobs_requiring"], -a["importance"]))[:8],
        "charts": {"score_trend": trend,
                   "job_compat": [{"job": jobs[m["job_id"]]["title"], "compatibility": m["compatibility"]} for m in matches[:8] if m["job_id"] in jobs],
                   "skills_by_area": [{"area": a, "count": c} for a, c in areas.most_common()]},
    }


@router.get("/admin")
def admin_dashboard(store=Depends(get_store), _: dict = Depends(require_admin)):
    scores = [float(v) for v in store.field_values("resumes", "resume_score") if v is not None]
    bins = [{"range": f"{i}-{i + 10}", "count": 0} for i in range(0, 100, 10)]
    for s in scores:
        bins[min(int(s // 10), 9)]["count"] += 1
    jobs, users = store.all("jobs"), store.all("users")
    cats = Counter(j["category"] for j in jobs)
    miss = Counter(m["skill"] for g in store.all("skill_gaps") for m in g["missing"])
    per_user = Counter(store.field_values("resumes", "user_id"))
    h = reference.get_reference()["hypothesis"]
    return {
        "stats": {"candidates": sum(1 for u in users if u["role"] == "candidate"), "resumes": sum(per_user.values()), "jobs": len(jobs),
                  "active_jobs": sum(1 for j in jobs if j.get("is_active", True)),
                  "avg_score": round(sum(scores) / len(scores), 1) if scores else 0, "evaluations": len(store.field_values("resume_evaluations", "resume_id"))},
        "score_distribution": bins,
        "jobs_by_category": [{"category": c, "count": n} for c, n in sorted(cats.items())],
        "top_missing_skills": [{"skill": s, "count": n} for s, n in miss.most_common(8)],
        "users": [{"id": u["id"], "full_name": u["full_name"], "email": u["email"], "role": u["role"], "is_active": u.get("is_active", True),
                   "resumes": per_user.get(u["id"], 0), "created_at": u["created_at"]} for u in newest_first(users)[:100]],
        "validation": {"n": h["n"], "proposed_accuracy": h["proposed"]["accuracy"], "baseline_accuracy": h["baseline"]["accuracy"],
                       "p_value": h["paired_t_test"]["p_value"], "significant": h["paired_t_test"]["significant"], "conclusion": h["conclusion"]},
    }
