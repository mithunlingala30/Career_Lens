"""Orchestration: load data, run the engine, persist results to Firestore."""
from fastapi import HTTPException

from ..algorithms import gaussian_analysis
from ..database import get_store, pair_id
from ..utils.helpers import to_native
from . import careers, reference, scoring
from .resume_service import profile_to_candidate
from .skills_taxonomy import suggestion_for


def load_jobs(active_only=True) -> list:
    jobs = get_store().all("jobs")
    if active_only:
        jobs = [j for j in jobs if j.get("is_active", True)]
    return [scoring.job_to_dict(j) for j in sorted(jobs, key=lambda j: j["id"])]


def candidate_for(resume: dict) -> dict:
    p = get_store().get("candidate_profiles", resume["id"])
    if not p:
        raise HTTPException(409, "Extract resume information first (POST /api/analysis/extract/{id})")
    return profile_to_candidate(p)


def reference_scores():
    vals = [float(v) for v in get_store().field_values("resumes", "resume_score") if v is not None]
    if len(vals) >= 20:
        return vals, f"platform candidates (n={len(vals)})"
    ref = reference.get_reference()["quality_scores"]
    return ref, f"reference cohort (n={len(ref)})"


def log_history(resume, event_type, title, scores, evaluation_id=None, job_id=None, batch=None):
    doc = {"user_id": resume["user_id"], "resume_id": resume["id"], "evaluation_id": evaluation_id, "job_id": job_id,
           "resume_name": resume["original_filename"], "event_type": event_type, "title": title, "scores": to_native(scores)}
    return (batch or get_store()).create("evaluation_history", doc)


def eval_doc(resume, r, quality, breakdown, gauss) -> dict:
    return {"id": pair_id(resume["id"], r["job_id"]), "user_id": resume["user_id"], "resume_id": resume["id"], "job_id": r["job_id"],
            "resume_score": quality, "compatibility": r["compatibility"], "skill_score": r["skill_score"],
            "education_score": r["education_score"], "experience_score": r["experience_score"],
            "probability_score": r["probability_score"], "latent_score": r["latent_score"],
            "bayes_posterior": r["bayes"]["posterior"], "conditional_probability": r["conditional"]["p_conditional"],
            "inner_product": r["inner_product"]["inner_product"], "cosine_similarity": r["inner_product"]["cosine"],
            "svd_similarity": r["svd"]["similarity"],
            "details": to_native({**r, "resume_score": quality, "resume_breakdown": breakdown, "gaussian": gauss})}


def run_matching(resume: dict) -> list:
    st, rid = get_store(), resume["id"]
    cand, jobs = candidate_for(resume), load_jobs()
    if not jobs:
        raise HTTPException(400, "No active jobs available - ask an admin to add jobs")
    table = reference.get_reference()["table"]
    svd = scoring.svd_for(cand, jobs)
    quality, breakdown = scoring.resume_quality(cand)
    refs, src = reference_scores()
    gauss = gaussian_analysis.analyze(quality, refs, src)
    results = sorted((scoring.evaluate(cand, j, jobs, table, svd) for j in jobs), key=lambda r: -r["compatibility"])
    for col in ("job_matches", "skill_gaps", "resume_evaluations"):
        st.delete_where(col, resume_id=rid)
    b = st.batch()
    for rank, r in enumerate(results, 1):
        pid = pair_id(rid, r["job_id"])
        b.put("resume_evaluations", eval_doc(resume, r, quality, breakdown, gauss))
        b.put("job_matches", {"id": pid, "user_id": resume["user_id"], "resume_id": rid, "job_id": r["job_id"], "compatibility": r["compatibility"],
                              "rank": rank, "matched_count": len(r["matched_skills"]), "missing_count": len(r["missing_skills"]),
                              "details": to_native({"matched_skills": r["matched_skills"], "missing_skills": r["missing_skills"],
                                                    "score_components": r["score_components"], "education_match": r["education_match"],
                                                    "experience_match": r["experience_match"]})})
        b.put("skill_gaps", {"id": pid, "resume_id": rid, "job_id": r["job_id"],
                             "matched": [{"skill": m["skill"], "importance": m["importance"]} for m in r["matched_skills"]],
                             "missing": [{"skill": m["skill"], "importance": m["importance"], "mandatory": m["mandatory"],
                                          "suggestion": suggestion_for(m["skill"])} for m in r["missing_skills"]]})
    top = results[0]
    log_history(resume, "matching", f"Matched against {len(results)} jobs",
                {"resume_score": quality, "top_job": top["job_title"], "top_compatibility": top["compatibility"],
                 "jobs_above_60": sum(1 for r in results if r["compatibility"] >= 60)}, job_id=top["job_id"], batch=b)
    b.put("resumes", {**resume, "resume_score": quality})
    b.commit()
    return results


def run_single_evaluation(resume: dict, job_id: int) -> dict:
    st = get_store()
    cand, jobs = candidate_for(resume), load_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        raise HTTPException(404, "Job not found or inactive")
    quality, breakdown = scoring.resume_quality(cand)
    refs, src = reference_scores()
    gauss = gaussian_analysis.analyze(quality, refs, src)
    r = scoring.evaluate(cand, job, jobs, reference.get_reference()["table"])
    b = st.batch()
    doc = b.put("resume_evaluations", eval_doc(resume, r, quality, breakdown, gauss))
    log_history(resume, "evaluation", f"Evaluated for {job['title']}",
                {"resume_score": quality, "compatibility": r["compatibility"], "job_title": job["title"],
                 "matched": len(r["matched_skills"]), "missing": len(r["missing_skills"])}, evaluation_id=doc["id"], job_id=job_id, batch=b)
    b.put("resumes", {**resume, "resume_score": quality})
    b.commit()
    return doc


def run_recommendations(resume: dict) -> list:
    st, rid = get_store(), resume["id"]
    cand, jobs = candidate_for(resume), load_jobs()
    if not jobs:
        raise HTTPException(400, "No active jobs available")
    recs = careers.recommend(cand, jobs, reference.get_reference()["table"], scoring.svd_for(cand, jobs))
    st.delete_where("career_recommendations", resume_id=rid)
    b = st.batch()
    for rank, r in enumerate(recs, 1):
        b.put("career_recommendations", to_native({"id": pair_id(rid, rank), "user_id": resume["user_id"], "resume_id": rid, "rank": rank, **r}))
    log_history(resume, "recommendation", f"Career recommendations: {recs[0]['category']} ranked first",
                {"top_category": recs[0]["category"], "suitability": recs[0]["suitability"], "readiness": recs[0]["readiness"]}, batch=b)
    b.commit()
    return recs
