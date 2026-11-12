"""
Evaluation engine: combines the mathematical modules into resume scores and job compatibility.

Compatibility (0-100) =  100 * [ 0.45 * skill coverage        (inner product)
                               + 0.10 * education fit
                               + 0.10 * experience fit
                               + 0.20 * suitability probability (mean of Bayes posterior and empirical conditional)
                               + 0.15 * latent fit              (SVD) ]
Resume quality score (0-100) is job-independent: completeness 15 + education 15 + skills 25 +
experience 20 + projects 10 + certifications 10 + summary 5.
"""
from ..algorithms import bayes_model, conditional_probability as cond, svd_analysis
from ..algorithms.inner_product import inner_product_match
from .skills_taxonomy import LEVELS, TAXONOMY, canonical

WEIGHTS = {"skills": 0.45, "education": 0.10, "experience": 0.10, "probability": 0.20, "latent": 0.15}


def make_candidate(skills: dict, edu_level: int, years: float, n_certs=0, n_projects=0, contact=None, has_summary=False,
                   n_education=None) -> dict:
    contact = contact or {"name": True, "email": True, "phone": True, "location": True}
    low = {k.lower(): float(v) for k, v in skills.items()}
    n_soft = sum(1 for k in skills if TAXONOMY.get(canonical(k), {}).get("type") == "non-technical")
    return {"skills": low, "display": {k.lower(): k for k in skills}, "edu_level": int(edu_level), "years": float(years),
            "n_certs": n_certs, "n_projects": n_projects, "contact": contact, "has_summary": has_summary,
            "n_soft": n_soft, "n_tech": len(skills) - n_soft}


def job_to_dict(job: dict) -> dict:
    reqs = job.get("requirements", [])
    return {"id": job["id"], "title": job["title"], "company": job.get("company", ""), "category": job["category"],
            "requirements": {r["skill_name"].lower(): int(r["importance"]) for r in reqs},
            "names": {r["skill_name"].lower(): r["skill_name"] for r in reqs},
            "mandatory": {r["skill_name"].lower() for r in reqs if r.get("is_mandatory")},
            "min_edu": int(job["min_education_level"]), "min_exp": float(job["min_experience_years"])}


def job_from_seed(j: dict, idx: int) -> dict:
    return {"id": -(idx + 1), "title": j["title"], "company": j["company"], "category": j["category"],
            "requirements": {canonical(s).lower(): i for s, i in j["requirements"]},
            "names": {canonical(s).lower(): canonical(s) for s, _ in j["requirements"]},
            "mandatory": {canonical(s).lower() for s in j["mandatory"]},
            "min_edu": j["min_education_level"], "min_exp": float(j["min_experience_years"])}


def features(cand: dict, job: dict) -> dict:
    ip = inner_product_match(cand["skills"], job["requirements"])
    req_e, lvl = job["min_edu"], cand["edu_level"]
    edu_ok = req_e == 0 or lvl >= req_e
    edu_score = 1.0 if edu_ok else lvl / req_e
    req_x, y = job["min_exp"], cand["years"]
    exp_score = 1.0 if req_x <= 0 else min(1.0, y / req_x)
    return {"ip": ip, "coverage": ip["coverage"], "edu_ok": edu_ok, "edu_score": edu_score,
            "exp_score": exp_score, "exp_ok": exp_score >= 0.6}


def svd_for(cand: dict, jobs: list) -> dict:
    return svd_analysis.latent_analysis({j["id"]: j["requirements"] for j in jobs}, cand["skills"], k=3)


def evaluate(cand: dict, job: dict, jobs: list, table: dict = None, svd: dict = None) -> dict:
    if table is None:
        from . import reference
        table = reference.get_reference()["table"]
    f = features(cand, job)
    evidence = [(imp, cand["skills"].get(s, 0.0)) for s, imp in job["requirements"].items()]
    bayes = bayes_model.posterior_suitability(evidence, f["edu_ok"], f["exp_score"])
    cp = cond.estimate(table, f["coverage"], f["edu_ok"], f["exp_ok"])
    p_blend = 0.5 * bayes["posterior"] + 0.5 * cp["p_conditional"]
    svd = svd or svd_for(cand, jobs)
    latent = svd["similarities"].get(job["id"], 0.0)
    parts = {"skills": f["coverage"], "education": f["edu_score"], "experience": f["exp_score"],
             "probability": p_blend, "latent": latent}
    compat = 100 * sum(WEIGHTS[k] * v for k, v in parts.items())
    matched, missing = [], []
    for s, imp in sorted(job["requirements"].items(), key=lambda kv: -kv[1]):
        name = job["names"].get(s, s)
        strength = cand["skills"].get(s, 0.0)
        if strength > 0:
            matched.append({"skill": name, "importance": imp, "strength": round(strength, 2),
                            "evidence": "demonstrated in experience/projects" if strength >= 1 else "listed in skills"})
        else:
            missing.append({"skill": name, "importance": imp, "mandatory": s in job["mandatory"]})
    labels = {"skills": "Skills (inner product)", "education": "Education fit", "experience": "Experience fit",
              "probability": "Suitability probability", "latent": "Latent fit (SVD)"}
    components = [{"key": k, "name": labels[k], "score": round(parts[k] * 100, 1), "weight": WEIGHTS[k],
                   "contribution": round(WEIGHTS[k] * parts[k] * 100, 1)} for k in WEIGHTS]
    return {
        "job_id": job["id"], "job_title": job["title"], "company": job.get("company", ""), "category": job["category"],
        "compatibility": round(compat, 1), "skill_score": round(f["coverage"] * 100, 1),
        "education_score": round(f["edu_score"] * 100, 1), "experience_score": round(f["exp_score"] * 100, 1),
        "probability_score": round(p_blend * 100, 1), "latent_score": round(latent * 100, 1),
        "matched_skills": matched, "missing_skills": missing, "score_components": components,
        "education_match": {"required_level": job["min_edu"], "required_label": LEVELS[job["min_edu"]],
                            "candidate_level": cand["edu_level"], "candidate_label": LEVELS[cand["edu_level"]],
                            "met": f["edu_ok"], "score": round(f["edu_score"] * 100, 1)},
        "experience_match": {"required_years": job["min_exp"], "candidate_years": cand["years"],
                             "met": f["exp_score"] >= 1.0, "score": round(f["exp_score"] * 100, 1)},
        "bayes": bayes, "conditional": cp,
        "inner_product": {k: v for k, v in f["ip"].items() if k != "contributions"} | {"top_contributions": sorted(
            f["ip"]["contributions"], key=lambda c: -c["product"])[:8]},
        "svd": {"similarity": latent, "k": svd["k"], "explained_variance": svd["explained_variance"],
                "cumulative_variance": svd.get("cumulative_variance", 0), "factors": svd["factors"],
                "candidate_latent": svd.get("candidate_latent", []), "job_latent": svd.get("job_latent", {}).get(job["id"], [])},
    }


def resume_quality(cand: dict):
    c = cand["contact"]
    contact = 4 * c.get("name", False) + 4 * c.get("email", False) + 4 * c.get("phone", False) + 3 * c.get("location", False)
    edu = {0: 0, 1: 6, 2: 11, 3: 14, 4: 15}[cand["edu_level"]]
    skills = min(1, cand["n_tech"] / 10) * 18 + min(1, cand["n_soft"] / 3) * 7
    exp = min(1, cand["years"] / 4) * 20
    proj = min(1, cand["n_projects"] / 3) * 10
    cert = min(1, cand["n_certs"] / 2) * 10
    summ = 5 if cand["has_summary"] else 0
    items = [("Contact completeness", contact, 15), ("Education", edu, 15), ("Skills breadth", skills, 25),
             ("Experience", exp, 20), ("Projects", proj, 10), ("Certifications", cert, 10), ("Profile summary", summ, 5)]
    total = round(sum(v for _, v, _ in items), 1)
    return total, [{"name": n, "score": round(v, 1), "max": m} for n, v, m in items]
