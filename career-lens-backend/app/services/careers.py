"""Career recommendation, readiness and progression (Bayes + inner product + Markov chain)."""
from ..algorithms import bayes_model, markov_chain
from ..algorithms.inner_product import inner_product_match
from . import scoring
from .seed import CAREER_LADDERS
from .skills_taxonomy import AREA_TIPS, area_of, suggestion_for

RUNG = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3}


def recommend(cand: dict, jobs: list, table: dict, svd: dict) -> list:
    evals = {j["id"]: scoring.evaluate(cand, j, jobs, table, svd) for j in jobs}
    cats = {}
    for j in jobs:
        cats.setdefault(j["category"], []).append(j)
    recs = []
    for cat, cjobs in cats.items():
        # category skill profile: mean importance across the category's jobs (absent skill = 0)
        agg, names = {}, {}
        for j in cjobs:
            for s, imp in j["requirements"].items():
                agg[s] = agg.get(s, 0) + imp
                names[s] = j["names"].get(s, s)
        agg = {s: v / len(cjobs) for s, v in agg.items()}
        core = dict(sorted(agg.items(), key=lambda kv: -kv[1])[:10])
        req_int = {s: max(1, round(v)) for s, v in core.items()}
        ip = inner_product_match(cand["skills"], req_int)
        post = bayes_model.posterior_suitability(
            [(imp, cand["skills"].get(s, 0.0)) for s, imp in req_int.items()],
            edu_ok=cand["edu_level"] >= min(j["min_edu"] for j in cjobs),
            exp_ratio=min(1.0, cand["years"] / max(0.5, sum(j["min_exp"] for j in cjobs) / len(cjobs))))["posterior"]
        readiness = 100 * (0.6 * ip["coverage"] + 0.4 * post)
        compats = [evals[j["id"]]["compatibility"] for j in cjobs]
        suitability = 0.7 * max(compats) + 0.3 * (sum(compats) / len(compats))
        required = [{"skill": names[s], "importance": req_int[s], "has": cand["skills"].get(s, 0) > 0} for s in core]
        missing = [r for r in required if not r["has"]]
        existing = [r["skill"] for r in required if r["has"]]
        areas = {}
        for m in missing:
            areas.setdefault(area_of(m["skill"]), []).append(m["skill"])
        learning = [{"area": a, "skills": sk, "tip": AREA_TIPS.get(a, "build a portfolio project that applies these skills")}
                    for a, sk in areas.items()]
        mk = markov_chain.analyze(readiness / 100, len(missing))
        ladder = CAREER_LADDERS.get(cat, ["Entry level", "Professional", "Senior", "Lead"])
        tips = [suggestion_for(m["skill"]) for m in missing[:4]]
        if mk["expected_months_to_target"] is not None:
            tips.append(f"At your current pace the Markov model expects about {mk['expected_months_to_target']} months to reach "
                        f"'{mk['target_state_name']}'. Closing the top gaps raises the monthly advance probability.")
        if cand["n_projects"] < 2: tips.append("Add at least two projects with measurable outcomes to strengthen evidence.")
        if cand["n_certs"] == 0: tips.append("Earn one recognised certification in this field to signal commitment.")
        recs.append({"category": cat, "suitability": round(suitability, 1), "readiness": round(readiness, 1),
                     "required_skills": required, "existing_skills": existing, "missing_skills": missing,
                     "learning_areas": learning,
                     "progression": {"ladder": ladder, "current_rung": RUNG[mk["current_state"]], "markov": mk,
                                     "development_suggestions": tips,
                                     "roles": [{"title": j["title"], "compatibility": evals[j["id"]]["compatibility"]} for j in cjobs]}})
    recs.sort(key=lambda r: -r["suitability"])
    return recs
