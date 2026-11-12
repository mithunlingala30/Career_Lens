"""End-to-end workflow test (uses a throw-away local JSON store, same interface as Firestore):  python -m tests.test_workflow"""
import io, os, tempfile
tmp = tempfile.mkdtemp()
os.environ["DB_BACKEND"] = "local"
os.environ["LOCAL_DB_PATH"] = f"{tmp}/db.json"
os.environ["UPLOAD_DIR"] = f"{tmp}/resumes"

from docx import Document
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.main import app

RESUME = """Priya Ramesh
priya.ramesh@example.com | +91 98765 43210 | Coimbatore, Tamil Nadu

SUMMARY
Backend developer with hands-on experience building REST APIs and data pipelines, a quick learner and strong team player.

EDUCATION
B.E. Computer Science and Engineering
PSG College of Technology, Coimbatore | 2018 - 2022 | CGPA: 8.4

EXPERIENCE
Software Engineer, Zoho Corporation | Jul 2022 - Present
- Built REST APIs with Python, FastAPI and PostgreSQL serving 2M requests a day
- Containerised services with Docker and automated deployments with Jenkins CI/CD
Intern - Backend Developer at TechSpark | Jan 2022 - Jun 2022
- Developed Django services and wrote unit testing suites using pytest

SKILLS
Python, SQL, FastAPI, Django, PostgreSQL, Docker, Git, Linux, Communication, Teamwork

PROJECTS
Smart Attendance System
- Face recognition attendance app using Python, OpenCV and Flask
Expense Tracker API
- Built with FastAPI, PostgreSQL and Docker

CERTIFICATIONS
AWS Certified Cloud Practitioner - Amazon 2023
Python for Everybody - Coursera 2021
"""


def docx_bytes(text):
    d = Document()
    for line in text.split("\n"):
        d.add_paragraph(line)
    b = io.BytesIO(); d.save(b); return b.getvalue()


def pdf_bytes(text):
    b = io.BytesIO(); c = canvas.Canvas(b); y = 800
    for line in text.split("\n"):
        c.drawString(40, y, line[:110]); y -= 14
        if y < 40: c.showPage(); y = 800
    c.save(); return b.getvalue()


with TestClient(app) as client:
    def H(t): return {"Authorization": f"Bearer {t}"}
    # --- auth
    assert client.post("/api/auth/register", json={"full_name": "Priya", "email": "priya@example.com", "password": "weak"}).status_code == 422
    r = client.post("/api/auth/register", json={"full_name": "Priya Ramesh", "email": "priya@example.com", "password": "Strong@123"})
    assert r.status_code == 201, r.text
    tok = r.json()["access_token"]
    assert client.post("/api/auth/register", json={"full_name": "Priya", "email": "priya@example.com", "password": "Strong@123"}).status_code == 409
    assert client.get("/api/auth/me", headers=H(tok)).json()["role"] == "candidate"
    assert client.post("/api/auth/login", json={"email": "priya@example.com", "password": "Strong@123", "role": "admin"}).status_code == 403
    adm = client.post("/api/auth/login", json={"email": "admin@careerlens.com", "password": "Admin@123", "role": "admin"})
    assert adm.status_code == 200, adm.text
    atok = adm.json()["access_token"]
    assert client.get("/api/dashboard/admin", headers=H(tok)).status_code == 403
    # --- upload (DOCX + PDF)
    assert client.post("/api/resumes/upload", headers=H(tok), files={"file": ("x.txt", b"hello", "text/plain")}).status_code == 400
    up = client.post("/api/resumes/upload", headers=H(tok), files={"file": ("priya.docx", docx_bytes(RESUME), "application/octet-stream")})
    assert up.status_code == 201, up.text
    rid = up.json()["id"]
    assert client.post("/api/resumes/upload", headers=H(tok), files={"file": ("priya.docx", docx_bytes(RESUME), "x")}).status_code == 409
    pdf = client.post("/api/resumes/upload", headers=H(tok), files={"file": ("priya.pdf", pdf_bytes(RESUME), "application/pdf")})
    assert pdf.status_code == 201, pdf.text
    pid = pdf.json()["id"]
    assert os.path.exists(f"{tmp}/resumes/" + up.json()["file_path"].split("/")[-1])
    # --- extract (both) and compare
    for rr in (rid, pid):
        p = client.post(f"/api/analysis/extract/{rr}", headers=H(tok)); assert p.status_code == 200, p.text
    p = client.get(f"/api/analysis/{rid}", headers=H(tok)).json()
    print("NAME", p["full_name"], "|", p["email"], "|", p["phone"], "|", p["location"])
    print("EDU", p["education"]); print("EXP", [(e["title"], e["company"], e["duration_months"]) for e in p["experience"]], p["total_experience_years"])
    print("SKILLS", [(s["skill_name"], s["evidence_weight"]) for s in p["skills"]])
    print("CERTS", p["certifications"]); print("PROJECTS", [(x["title"], x["technologies"]) for x in p["projects"]])
    pp = client.get(f"/api/analysis/{pid}", headers=H(tok)).json()
    print("PDF name/skills", pp["full_name"], len(pp["skills"]), pp["total_experience_years"])
    assert p["full_name"] == "Priya Ramesh" and p["email"] and p["highest_education_level"] == 2 and len(p["skills"]) >= 10
    # --- edit profile
    body = {k: p[k] for k in ("full_name", "email", "phone", "location", "summary")}
    body.update({k: [{kk: vv for kk, vv in it.items() if kk not in ("id", "area", "evidence_weight")} for it in p[k]] for k in ("skills", "education", "experience", "certifications", "projects")})
    body["skills"].append({"skill_name": "Kubernetes", "skill_type": "technical"})
    u = client.put(f"/api/analysis/{rid}", headers=H(tok), json=body); assert u.status_code == 200, u.text
    assert any(s["skill_name"] == "Kubernetes" for s in u.json()["skills"]) and u.json()["is_edited"]
    # --- matching / evaluation / recommendations
    m = client.post(f"/api/matching/{rid}", headers=H(tok)); assert m.status_code == 200, m.text
    ms = m.json()["matches"]
    print("TOP MATCHES", [(x["job"]["title"], x["compatibility"]) for x in ms[:5]])
    assert ms[0]["compatibility"] >= ms[-1]["compatibility"] and len(ms) == 15
    jid = ms[0]["job"]["id"]
    e = client.post(f"/api/evaluation/{rid}/{jid}", headers=H(tok)); assert e.status_code == 200, e.text
    ev = e.json()
    print("EVAL", ev["resume_score"], ev["compatibility"], ev["bayes"]["posterior"], ev["conditional"]["p_conditional"], ev["svd"]["similarity"], ev["gaussian"]["percentile"])
    assert 0 <= ev["resume_score"] <= 100 and 0 <= ev["compatibility"] <= 100
    assert client.get(f"/api/evaluation/{rid}", headers=H(tok)).json()
    assert client.get(f"/api/evaluation/{rid}?job_id={jid}", headers=H(tok)).json()["job_id"] == jid
    rec = client.post(f"/api/recommendations/{rid}", headers=H(tok)); assert rec.status_code == 200, rec.text
    rs = rec.json()["recommendations"]
    print("RECS", [(r["category"], r["suitability"], r["readiness"], r["progression"]["markov"]["current_state_name"], r["progression"]["markov"]["expected_months_to_target"]) for r in rs[:4]])
    sg = client.get(f"/api/skill-gaps/{rid}", headers=H(tok)); assert sg.status_code == 200, sg.text
    print("GAPS", sg.json()["coverage"], [m["skill"] for m in sg.json()["missing"][:5]])
    assert client.get(f"/api/skill-gaps/{rid}?job_id={ms[3]['job']['id']}", headers=H(tok)).json()["selected_job_id"] == ms[3]["job"]["id"]
    # --- dashboards, history, report
    d = client.get("/api/dashboard/candidate", headers=H(tok)); assert d.status_code == 200, d.text
    print("DASH", d.json()["stats"])
    h = client.get("/api/evaluation/history", headers=H(tok)).json(); print("HISTORY", [x["event_type"] for x in h])
    rp = client.get(f"/api/reports/{ev['id']}/pdf", headers=H(tok)); assert rp.status_code == 200 and rp.content[:4] == b"%PDF", rp.text[:200]
    print("PDF bytes", len(rp.content))
    assert client.get("/api/evaluation/validation", headers=H(tok)).json()["paired_t_test"]
    assert client.get(f"/api/resumes/{rid}/file", headers=H(tok)).status_code == 200
    # --- admin job CRUD
    jb = {"title": "Rust Systems Engineer", "company": "Ferrous", "category": "Software Development", "description": "You must know Rust and Linux. Docker is a plus. Strong communication required.", "min_education_level": 2, "min_experience_years": 1}
    assert client.post("/api/jobs", headers=H(tok), json=jb).status_code == 403
    c = client.post("/api/jobs", headers=H(atok), json=jb); assert c.status_code == 201, c.text
    print("AUTO REQS", c.json()["requirements"])
    assert client.post("/api/jobs", headers=H(atok), json=jb).status_code == 409
    jid2 = c.json()["id"]
    assert client.put(f"/api/jobs/{jid2}", headers=H(atok), json={**jb, "company": "Ferrous Inc"}).status_code == 200
    assert client.get("/api/jobs?q=rust", headers=H(tok)).json()
    assert client.put("/api/jobs/categories/rename", headers=H(atok), json={"old": "Marketing", "new": "Growth Marketing"}).status_code == 200
    ad = client.get("/api/dashboard/admin", headers=H(atok)); assert ad.status_code == 200, ad.text
    print("ADMIN", ad.json()["stats"])
    assert client.delete(f"/api/jobs/{jid2}", headers=H(atok)).status_code == 200
    # --- forgot password
    f = client.post("/api/auth/forgot-password", json={"email": "priya@example.com"}).json()
    assert client.post("/api/auth/reset-password", json={"token": f["dev_reset_token"], "new_password": "Newpass@123"}).status_code == 200
    assert client.post("/api/auth/login", json={"email": "priya@example.com", "password": "Newpass@123"}).status_code == 200
    # --- isolation + delete
    other = client.post("/api/auth/register", json={"full_name": "Other", "email": "o@example.com", "password": "Strong@123"}).json()["access_token"]
    assert client.get(f"/api/resumes/{rid}", headers=H(other)).status_code == 404
    assert client.delete(f"/api/resumes/{rid}", headers=H(tok)).status_code == 200
    assert client.get("/api/evaluation/history", headers=H(tok)).json()
    # --- every stored document must be valid for Firestore (no nested arrays, <1 MiB, simple types, safe keys)
    import json
    from app.database import get_store
    def walk(x, path, in_list=False):
        if isinstance(x, list):
            assert not in_list, f"nested array at {path}"
            for i in x: walk(i, path, True)
        elif isinstance(x, dict):
            for k, v in x.items():
                assert k and "/" not in k and not (k.startswith("__") and k.endswith("__")), f"bad key {k!r} at {path}"
                walk(v, f"{path}.{k}")
        else:
            assert x is None or isinstance(x, (str, int, float, bool)), f"bad type {type(x)} at {path}"
    n = 0
    for col, docs in get_store().data.items():
        for d in docs.values():
            walk(d, col); n += 1
            assert len(json.dumps(d)) < 900_000, f"{col} document too large"
    print(f"FIRESTORE-SAFETY: {n} stored documents validated")
    print("ALL WORKFLOW CHECKS PASSED")
