"""Resume text extraction (PyMuPDF / python-docx) and rule-based information extraction."""
import re
from datetime import date

try:
    import pymupdf as fitz  # PyMuPDF >= 1.24.3
except ImportError:  # older releases
    import fitz
from docx import Document

from .skills_taxonomy import TAXONOMY, find_skills

# ---------------------------------------------------------------- text extraction
def extract_text(path: str, file_type: str) -> str:
    if file_type == "pdf":
        with fitz.open(path) as doc:
            text = "\n".join(page.get_text() for page in doc)
    else:
        d = Document(path)
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                parts.append(" | ".join(c.text.strip() for c in row.cells))
        text = "\n".join(parts)
    text = text.replace("\r", "\n").replace("\u00a0", " ")
    return re.sub(r"[ \t]+", " ", text).strip()


# ---------------------------------------------------------------- sections
HEADERS = {
    "summary": {"summary", "profile", "professional summary", "objective", "career objective", "about me", "profile summary"},
    "education": {"education", "academic background", "educational qualifications", "academics", "education and training", "qualifications"},
    "experience": {"experience", "work experience", "professional experience", "employment history", "internship", "internships", "work history", "internship experience"},
    "skills": {"skills", "technical skills", "core competencies", "key skills", "skills and tools", "soft skills", "technical proficiency", "competencies", "skills summary"},
    "certifications": {"certifications", "certificates", "licenses and certifications", "courses", "certifications and courses", "training and certifications"},
    "projects": {"projects", "academic projects", "personal projects", "key projects", "project work", "projects and achievements"},
}
HEADER_LOOKUP = {alias: sec for sec, al in HEADERS.items() for alias in al}


def _header_of(line: str):
    norm = re.sub(r"\s+", " ", re.sub(r"[^a-z& ]", " ", line.lower()).replace("&", "and")).strip()
    return HEADER_LOOKUP.get(norm) if len(line) <= 40 else None


def split_sections(text: str) -> dict:
    sections, cur = {"header": []}, "header"
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            sections.setdefault(cur, []).append("")
            continue
        h = _header_of(line)
        if h:
            cur = h
            sections.setdefault(cur, [])
        else:
            sections.setdefault(cur, []).append(line)
    return sections


# ---------------------------------------------------------------- contact
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")
CITIES = ["Coimbatore", "Chennai", "Bengaluru", "Bangalore", "Hyderabad", "Mumbai", "Pune", "New Delhi", "Delhi", "Kolkata",
          "Ahmedabad", "Kochi", "Madurai", "Trichy", "Tiruchirappalli", "Salem", "Tiruppur", "Noida", "Gurgaon", "Gurugram",
          "Jaipur", "Chandigarh", "Mysore", "Mysuru", "Thiruvananthapuram", "Visakhapatnam", "London", "New York", "San Francisco",
          "Seattle", "Austin", "Boston", "Toronto", "Dubai", "Singapore", "Sydney", "Berlin", "Remote"]
CITY_RE = re.compile(r"\b(%s)\b(?:\s*,\s*[A-Z][A-Za-z .]{1,25})?" % "|".join(CITIES))


def extract_contact(text: str, header_lines: list) -> dict:
    head = "\n".join(l for l in text.split("\n")[:15])
    email = (EMAIL_RE.search(text) or [None])[0] if EMAIL_RE.search(text) else ""
    phone = ""
    for m in PHONE_RE.finditer(head) or []:
        digits = re.sub(r"\D", "", m.group(1))
        if 10 <= len(digits) <= 13 and not re.fullmatch(r"(19|20)\d{2}\D*(19|20)\d{2}", m.group(1).strip()):
            phone = m.group(1).strip(); break
    if not phone:
        for m in PHONE_RE.finditer(text):
            digits = re.sub(r"\D", "", m.group(1))
            if 10 <= len(digits) <= 13:
                phone = m.group(1).strip(); break
    location = ""
    lm = re.search(r"(?:Location|Address|Based in)\s*[:\-]\s*([^\n|]{3,60})", head, re.I)
    if lm:
        location = lm.group(1).strip()
    else:
        cm = CITY_RE.search(head)
        if cm:
            location = cm.group(0).strip(" ,")
    name = ""
    for line in [l.strip() for l in text.split("\n") if l.strip()][:6]:
        clean = re.sub(r"^(name\s*[:\-]\s*)", "", line, flags=re.I)
        words = clean.split()
        if (1 < len(words) <= 4 and not re.search(r"[\d@:/|]", clean) and all(re.fullmatch(r"[A-Za-z.'-]+", w) for w in words)
                and not _header_of(clean) and clean.lower() not in ("curriculum vitae", "resume")):
            name = clean.title() if clean.isupper() or clean.islower() else clean
            break
    if not name and email:
        name = re.sub(r"[._\d]+", " ", email.split("@")[0]).strip().title()
    return {"full_name": name, "email": email, "phone": phone, "location": location}


# ---------------------------------------------------------------- education
_FULL = [(4, r"doctorate|ph\.?\s?d"), (3, r"master(?:'s|s)?|post[- ]?graduate|m\.?\s?tech"),
         (2, r"bachelor(?:'s|s)?|under[- ]?graduate|b\.?\s?tech"), (1, r"diploma|polytechnic")]
_ABBR = [(4, r"Ph\.?D\.?"), (3, r"M\.?Tech|M\.?Sc\.?|MBA|MCA|M\.?Com\.?|M\.?E\.?|ME|M\.?S\.?|MS|M\.?A\.?|MA"),
         (2, r"B\.?Tech|B\.?E\.?|BE|B\.?Sc\.?|BCA|B\.?Com\.?|BBA|B\.?A\.?|BA|B\.?S\.?|BS|B\.?Des")]
LEVEL_FULL = [(lv, re.compile(r"(?<![A-Za-z])(?:%s)(?![A-Za-z])" % p, re.I)) for lv, p in _FULL]
LEVEL_ABBR = [(lv, re.compile(r"(?<![A-Za-z])(?:%s)(?![A-Za-z])" % p)) for lv, p in _ABBR]
INSTITUTION_RE = re.compile(r"(University|College|Institute|School|Academy|IIT|NIT|IIM|Polytechnic)", re.I)
FIELDS = ["Computer Science", "Information Technology", "Electronics and Communication", "Electronics", "Electrical", "Mechanical",
          "Civil", "Data Science", "Artificial Intelligence", "Software Engineering", "Business Administration", "Commerce",
          "Mathematics", "Statistics", "Physics", "Design", "Cyber Security", "Computer Applications", "Marketing", "Finance"]
GRADE_RE = re.compile(r"(?:CGPA|GPA|CPI)\s*[:\-]?\s*\d+(?:\.\d+)?(?:\s*/\s*\d+)?|\d{2,3}(?:\.\d+)?\s?%")


def degree_level(line: str, strict: bool = True):
    for lv, rx in LEVEL_FULL:
        m = rx.search(line)
        if m:
            return lv, m.group(0)
    if strict:
        for lv, rx in LEVEL_ABBR:
            m = rx.search(line)
            if m:
                return lv, m.group(0)
    return 0, ""


def parse_education(lines: list) -> list:
    out, i = [], 0
    lines = [l for l in lines if l]
    while i < len(lines):
        lv, deg = degree_level(lines[i])
        if lv:
            window = lines[i:i + 3]
            blob = " ".join(window)
            inst = ""
            for w in window:
                if INSTITUTION_RE.search(w):
                    seg = [s.strip() for s in re.split(r"[|,–—]| - ", w) if INSTITUTION_RE.search(s)]
                    inst = (seg[0] if seg else w).strip(); break
            field = next((f for f in FIELDS if f.lower() in blob.lower()), "")
            years = [int(y) for y in re.findall(r"(?:19|20)\d{2}", blob)]
            grade = (GRADE_RE.search(blob) or [""])[0] if GRADE_RE.search(blob) else ""
            out.append({"degree": deg.strip(), "field_of_study": field, "institution": inst[:200],
                        "start_year": min(years) if len(years) > 1 else None,
                        "end_year": max(years) if years else None, "grade": grade, "level": lv})
            i += 2 if inst and not INSTITUTION_RE.search(lines[i]) else 1
        else:
            i += 1
    return out


# ---------------------------------------------------------------- experience
MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
DATE = r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4}|\d{1,2}/\d{4}|\d{4})"
RANGE_RE = re.compile(rf"({DATE})\s*(?:-|–|—|to|until)\s*({DATE}|Present|Current|Now|Ongoing|Till date)", re.I)
PRESENT = {"present", "current", "now", "ongoing", "till date"}


def parse_date(s: str, is_end: bool):
    s = s.strip().lower().rstrip(",")
    if s in PRESENT:
        t = date.today(); return t.year, t.month
    m = re.match(r"([a-z]{3})[a-z]*\.?,?\s+(\d{4})", s)
    if m and m.group(1) in MONTHS:
        return int(m.group(2)), MONTHS[m.group(1)]
    m = re.match(r"(\d{1,2})/(\d{4})", s)
    if m:
        return int(m.group(2)), max(1, min(12, int(m.group(1))))
    m = re.match(r"(\d{4})", s)
    return (int(m.group(1)), 12 if is_end else 1) if m else None


def years_from_entries(entries: list) -> float:
    """Merge overlapping date intervals so concurrent jobs aren't double counted."""
    spans, extra = [], 0
    for e in entries:
        s = parse_date(e.get("start_date") or "", False) if e.get("start_date") else None
        en = parse_date(e.get("end_date") or "", True) if e.get("end_date") else None
        if s and en:
            spans.append((s[0] * 12 + s[1], en[0] * 12 + en[1]))
        else:
            extra += int(e.get("duration_months") or 0)
    spans.sort(); total, cur = 0, None
    for a, b in spans:
        if cur is None: cur = [a, b]
        elif a <= cur[1]: cur[1] = max(cur[1], b)
        else: total += cur[1] - cur[0] + 1; cur = [a, b]
    if cur: total += cur[1] - cur[0] + 1
    return round((total + extra) / 12, 1)


def parse_experience(lines: list) -> list:
    idx = [i for i, l in enumerate(lines) if l and RANGE_RE.search(l)]
    out = []
    for n, i in enumerate(idx):
        m = RANGE_RE.search(lines[i])
        s, e = m.group(1), m.group(2)
        head = re.sub(r"[()\[\]|•·]", " ", RANGE_RE.sub("", lines[i])).strip(" -–—,:")
        prev = lines[i - 1] if i > 0 and lines[i - 1] and (n == 0 or idx[n - 1] != i - 1) else ""
        if len(head) < 3 and prev:
            head = prev
        splitter = r"\s+(?:at|@)\s+" if re.search(r"\s(?:at|@)\s", head) else r"\s*[|–—]\s*|\s+-\s+|,\s*"
        parts = [p.strip(" -–—") for p in re.split(splitter, head) if p.strip(" -–—")]
        title = parts[0] if parts else "Role"
        company = parts[1] if len(parts) > 1 else ""
        end_i = idx[n + 1] - 1 if n + 1 < len(idx) else len(lines)
        desc = " ".join(l.lstrip("•-* ") for l in lines[i + 1:end_i] if l)[:900]
        a, b = parse_date(s, False), parse_date(e, True)
        months = max(1, (b[0] - a[0]) * 12 + (b[1] - a[1]) + 1) if a and b else 0
        out.append({"title": title[:150], "company": company[:150], "start_date": s.strip(), "end_date": e.strip(),
                    "duration_months": min(months, 600), "description": desc})
    return out


# ---------------------------------------------------------------- certifications / projects
ISSUERS = ["Coursera", "Udemy", "AWS", "Amazon", "Microsoft", "Google", "Oracle", "Cisco", "NPTEL", "IBM", "Meta", "edX",
           "Infosys", "Red Hat", "Salesforce", "HackerRank", "LinkedIn", "PMI", "Udacity", "Great Learning"]
CERT_HINT = re.compile(r"certif|certificate|\bPMP\b|CCNA|NPTEL", re.I)


def parse_certifications(sec_lines: list, all_lines: list) -> list:
    cands = [l for l in sec_lines if l]
    if not cands:
        cands = [l for l in all_lines if CERT_HINT.search(l) and len(l) < 140]
    out, seen = [], set()
    for l in cands:
        name = l.lstrip("•-*· ").strip()
        if len(name) < 4 or name.lower() in seen:
            continue
        seen.add(name.lower())
        issuer = next((x for x in ISSUERS if x.lower() in name.lower()), "")
        year = (re.search(r"(?:19|20)\d{2}", name) or [""])[0] if re.search(r"(?:19|20)\d{2}", name) else ""
        out.append({"name": name[:200], "issuer": issuer, "year": year})
    return out[:15]


def parse_projects(lines: list) -> list:
    out, cur = [], None
    for l in lines:
        if not l:
            continue
        is_bullet = l[0] in "•-*·–" or l.lower().startswith(("tech", "built", "developed", "implemented", "designed", "created", "using"))
        if not is_bullet and len(l) < 90 and (cur is None or cur["description"] or len(cur["title"]) > 0):
            if cur: out.append(cur)
            cur = {"title": re.split(r"\s*[|:–—]\s*", l)[0].strip(" -")[:200], "description": "", "technologies": ""}
            rest = re.split(r"\s*[|:–—]\s*", l, maxsplit=1)
            if len(rest) > 1: cur["description"] = rest[1]
        elif cur is not None:
            cur["description"] = (cur["description"] + " " + l.lstrip("•-*·– ")).strip()
        else:
            cur = {"title": l.lstrip("•-*·– ")[:80], "description": "", "technologies": ""}
    if cur: out.append(cur)
    for p in out:
        text = f"{p['title']} {p['description']}"
        p["technologies"] = ", ".join(find_skills(text).keys())[:400]
        p["description"] = p["description"][:900]
    return [p for p in out if p["title"]][:12]


# ---------------------------------------------------------------- skills
def skill_weights(skills_text: str, evidence_text: str, other_text: str = "") -> dict:
    """Evidence strength: 1.0 when a skill is demonstrated in experience/projects, 0.7 if only listed."""
    ev = find_skills(evidence_text)
    allf = find_skills(skills_text + "\n" + evidence_text + "\n" + other_text)
    return {s: (1.0 if s in ev else 0.7) for s in allf}


def parse_skills(sections: dict, full_text: str) -> list:
    evidence = "\n".join(sections.get("experience", []) + sections.get("projects", []))
    skills_text = "\n".join(sections.get("skills", []))
    found = skill_weights(skills_text, evidence, full_text)
    out = [{"skill_name": s, "skill_type": TAXONOMY[s]["type"], "evidence_weight": w} for s, w in found.items()]
    known = {a for d in TAXONOMY.values() for a in d["aliases"]} | {s.lower() for s in TAXONOMY}
    extra = []
    for line in sections.get("skills", []):
        body = line.split(":", 1)[1] if ":" in line[:30] else line
        for tok in re.split(r"[,|•·;/]|\s{2,}", body):
            tok = tok.strip(" -*•.")
            if 2 <= len(tok) <= 30 and len(tok.split()) <= 3 and re.fullmatch(r"[A-Za-z][A-Za-z0-9 .+#&-]*", tok) and tok.lower() not in known:
                extra.append(tok)
    have = {o["skill_name"].lower() for o in out}
    for t in extra[:25]:
        if t.lower() not in have:
            have.add(t.lower())
            out.append({"skill_name": t, "skill_type": "technical", "evidence_weight": 0.5})
    return out


# ---------------------------------------------------------------- orchestrator
def parse_resume(text: str) -> dict:
    sections = split_sections(text)
    all_lines = [l.strip() for l in text.split("\n") if l.strip()]
    contact = extract_contact(text, sections.get("header", []))
    edu_lines = sections.get("education", [])
    education = parse_education(edu_lines) if edu_lines else []
    if not education:
        education = [e for e in parse_education([l for l in all_lines if len(l) < 160]) ][:3]
    experience = parse_experience(sections.get("experience", []))
    years = years_from_entries(experience)
    if not experience:
        m = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience", text, re.I)
        years = float(m.group(1)) if m else 0.0
    summary = " ".join(sections.get("summary", []))[:600]
    return {
        **contact, "summary": summary,
        "skills": parse_skills(sections, text), "education": education, "experience": experience,
        "certifications": parse_certifications(sections.get("certifications", []), all_lines),
        "projects": parse_projects(sections.get("projects", [])),
        "total_experience_years": years,
        "highest_education_level": max([e["level"] for e in education], default=0),
    }


# ---------------------------------------------------------------- job description analysis
def extract_job_skills(description: str) -> list:
    """Derive required skills + importance (1-5) from a job description."""
    counts, required, optional = {}, set(), set()
    for sent in re.split(r"\n|;|(?<=[a-z0-9])\.\s+", description):
        found = find_skills(sent)
        low = sent.lower()
        for s, c in found.items():
            counts[s] = counts.get(s, 0) + c
            if re.search(r"must|required|mandatory|essential|strong|proficien", low): required.add(s)
            if re.search(r"preferred|nice to have|a plus|bonus|good to have", low): optional.add(s)
    out = []
    for s, c in counts.items():
        imp = 5 if c >= 3 else 4 if c == 2 else 3
        if s in required: imp = min(5, imp + 1)
        if s in optional: imp = max(1, imp - 1)
        out.append({"skill_name": s, "importance": imp, "is_mandatory": s in required and imp >= 4})
    return sorted(out, key=lambda x: -x["importance"])
