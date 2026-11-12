"""Build / read candidate-profile documents (skills, education, experience, certifications and projects are embedded)."""
from . import scoring
from .resume_parser import years_from_entries
from .skills_taxonomy import TAXONOMY, area_of, canonical


def make_profile(resume: dict, data: dict, parsed_years=None, old_weights=None, edited=False, existing=None) -> dict:
    seen, skills = set(), []
    for s in data.get("skills", []):
        name = canonical(s["skill_name"])
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        info = TAXONOMY.get(name)
        w = s.get("evidence_weight")
        if w is None:
            w = (old_weights or {}).get(name, 0.7)
        skills.append({"skill_name": name[:80], "skill_type": info["type"] if info else s.get("skill_type", "technical"),
                       "evidence_weight": float(w), "source": s.get("source", "extracted")})
    education = [{"degree": e["degree"], "field_of_study": e.get("field_of_study") or "", "institution": e.get("institution") or "",
                  "start_year": e.get("start_year"), "end_year": e.get("end_year"), "grade": e.get("grade") or "",
                  "level": int(e.get("level") or 0)} for e in data.get("education", [])]
    experience = [{"title": e["title"], "company": e.get("company") or "", "start_date": e.get("start_date") or "", "end_date": e.get("end_date") or "",
                   "duration_months": int(e.get("duration_months") or 0), "description": e.get("description") or ""} for e in data.get("experience", [])]
    return {
        **(existing or {}), "id": resume["id"], "resume_id": resume["id"], "user_id": resume["user_id"],
        **{f: (data.get(f) or "").strip() for f in ("full_name", "email", "phone", "location", "summary")},
        "skills": skills, "education": education, "experience": experience,
        "certifications": [{"name": c["name"], "issuer": c.get("issuer") or "", "year": str(c.get("year") or "")} for c in data.get("certifications", [])],
        "projects": [{"title": p["title"], "description": p.get("description") or "", "technologies": p.get("technologies") or ""} for p in data.get("projects", [])],
        "total_experience_years": float(parsed_years if parsed_years is not None else years_from_entries(experience)),
        "highest_education_level": max([e["level"] for e in education], default=0),
        "is_edited": edited,
    }


def profile_to_dict(p: dict) -> dict:
    out = {**p}
    out["skills"] = [{**s, "area": area_of(s["skill_name"])} for s in p.get("skills", [])]
    return out


def profile_to_candidate(p: dict) -> dict:
    return scoring.make_candidate(
        {s["skill_name"]: s["evidence_weight"] for s in p.get("skills", [])}, p.get("highest_education_level", 0), p.get("total_experience_years", 0),
        n_certs=len(p.get("certifications", [])), n_projects=len(p.get("projects", [])),
        contact={"name": bool(p.get("full_name")), "email": bool(p.get("email")), "phone": bool(p.get("phone")), "location": bool(p.get("location"))},
        has_summary=len((p.get("summary") or "").strip()) >= 30)


def resume_to_dict(r: dict) -> dict:
    return {"id": r["id"], "original_filename": r["original_filename"], "file_type": r["file_type"], "file_size": r["file_size"],
            "file_path": r["file_path"], "status": r["status"], "created_at": r["created_at"], "candidate_name": r.get("candidate_name", ""),
            "resume_score": r.get("resume_score")}
