"""Skill taxonomy used for resume parsing and job-description analysis."""
import re

LEVELS = {0: "Not specified", 1: "Diploma", 2: "Bachelor's", 3: "Master's", 4: "Doctorate"}

# (canonical name, area, type, match terms (lower-case))
_RAW = [
    ("Python", "Programming", "technical", ["python"]),
    ("Java", "Programming", "technical", ["java"]),
    ("JavaScript", "Programming", "technical", ["javascript", "js", "ecmascript", "es6"]),
    ("TypeScript", "Programming", "technical", ["typescript"]),
    ("C++", "Programming", "technical", ["c++", "cpp"]),
    ("C#", "Programming", "technical", ["c#", "csharp", "c sharp"]),
    ("C", "Programming", "technical", ["c programming", "c language"]),
    ("Go", "Programming", "technical", ["golang", "go language"]),
    ("Rust", "Programming", "technical", ["rust"]),
    ("PHP", "Programming", "technical", ["php"]),
    ("Ruby", "Programming", "technical", ["ruby", "ruby on rails"]),
    ("Kotlin", "Programming", "technical", ["kotlin"]),
    ("Swift", "Programming", "technical", ["swift"]),
    ("Scala", "Programming", "technical", ["scala"]),
    ("MATLAB", "Programming", "technical", ["matlab"]),
    ("R", "Programming", "technical", ["r programming", "r language"]),
    ("HTML", "Web Development", "technical", ["html", "html5"]),
    ("CSS", "Web Development", "technical", ["css", "css3"]),
    ("React", "Web Development", "technical", ["react", "react.js", "reactjs"]),
    ("Angular", "Web Development", "technical", ["angular", "angularjs"]),
    ("Vue.js", "Web Development", "technical", ["vue", "vue.js", "vuejs"]),
    ("Next.js", "Web Development", "technical", ["next.js", "nextjs"]),
    ("Node.js", "Web Development", "technical", ["node.js", "nodejs"]),
    ("Express.js", "Web Development", "technical", ["express.js", "expressjs"]),
    ("Django", "Web Development", "technical", ["django"]),
    ("Flask", "Web Development", "technical", ["flask"]),
    ("FastAPI", "Web Development", "technical", ["fastapi"]),
    ("Spring Boot", "Web Development", "technical", ["spring boot", "springboot", "spring framework"]),
    ("Tailwind CSS", "Web Development", "technical", ["tailwind css", "tailwind", "tailwindcss"]),
    ("Bootstrap", "Web Development", "technical", ["bootstrap"]),
    ("REST APIs", "Web Development", "technical", ["rest api", "rest apis", "restful", "restful api", "restful apis"]),
    ("GraphQL", "Web Development", "technical", ["graphql"]),
    ("Machine Learning", "Data & AI", "technical", ["machine learning", "ml"]),
    ("Deep Learning", "Data & AI", "technical", ["deep learning", "neural networks"]),
    ("NLP", "Data & AI", "technical", ["nlp", "natural language processing"]),
    ("Computer Vision", "Data & AI", "technical", ["computer vision", "opencv"]),
    ("TensorFlow", "Data & AI", "technical", ["tensorflow", "keras"]),
    ("PyTorch", "Data & AI", "technical", ["pytorch"]),
    ("Scikit-learn", "Data & AI", "technical", ["scikit-learn", "sklearn", "scikit learn"]),
    ("Pandas", "Data & AI", "technical", ["pandas"]),
    ("NumPy", "Data & AI", "technical", ["numpy"]),
    ("Data Analysis", "Data & AI", "technical", ["data analysis", "data analytics"]),
    ("Data Visualization", "Data & AI", "technical", ["data visualization", "data visualisation"]),
    ("Statistics", "Data & AI", "technical", ["statistics", "statistical analysis", "statistical modeling", "statistical modelling"]),
    ("Power BI", "Data & AI", "technical", ["power bi", "powerbi"]),
    ("Tableau", "Data & AI", "technical", ["tableau"]),
    ("Excel", "Data & AI", "technical", ["excel", "ms excel", "microsoft excel", "advanced excel"]),
    ("Apache Spark", "Data & AI", "technical", ["apache spark", "pyspark"]),
    ("ETL", "Data & AI", "technical", ["etl", "data pipelines", "data pipeline"]),
    ("Generative AI", "Data & AI", "technical", ["generative ai", "llm", "llms", "large language models", "prompt engineering"]),
    ("Big Data", "Data & AI", "technical", ["big data", "hadoop"]),
    ("AWS", "Cloud & DevOps", "technical", ["aws", "amazon web services"]),
    ("Azure", "Cloud & DevOps", "technical", ["azure", "microsoft azure"]),
    ("Google Cloud", "Cloud & DevOps", "technical", ["google cloud", "gcp"]),
    ("Docker", "Cloud & DevOps", "technical", ["docker"]),
    ("Kubernetes", "Cloud & DevOps", "technical", ["kubernetes", "k8s"]),
    ("CI/CD", "Cloud & DevOps", "technical", ["ci/cd", "ci cd", "continuous integration", "continuous delivery"]),
    ("Jenkins", "Cloud & DevOps", "technical", ["jenkins"]),
    ("Git", "Cloud & DevOps", "technical", ["git", "github", "gitlab", "version control"]),
    ("Linux", "Cloud & DevOps", "technical", ["linux", "unix", "bash scripting"]),
    ("Terraform", "Cloud & DevOps", "technical", ["terraform", "infrastructure as code"]),
    ("Microservices", "Cloud & DevOps", "technical", ["microservices", "microservice"]),
    ("SQL", "Databases", "technical", ["sql", "t-sql", "pl/sql"]),
    ("PostgreSQL", "Databases", "technical", ["postgresql", "postgres"]),
    ("MySQL", "Databases", "technical", ["mysql"]),
    ("MongoDB", "Databases", "technical", ["mongodb", "mongo db"]),
    ("Redis", "Databases", "technical", ["redis"]),
    ("NoSQL", "Databases", "technical", ["nosql"]),
    ("Firebase", "Databases", "technical", ["firebase"]),
    ("Android", "Mobile", "technical", ["android", "android studio"]),
    ("iOS", "Mobile", "technical", ["ios", "iphone development"]),
    ("Flutter", "Mobile", "technical", ["flutter", "dart"]),
    ("React Native", "Mobile", "technical", ["react native"]),
    ("Cybersecurity", "Security & Networking", "technical", ["cybersecurity", "cyber security", "information security", "infosec"]),
    ("Networking", "Security & Networking", "technical", ["networking", "computer networks", "tcp/ip", "network administration"]),
    ("Penetration Testing", "Security & Networking", "technical", ["penetration testing", "pentest", "pen testing", "ethical hacking"]),
    ("UI/UX Design", "Design", "technical", ["ui/ux", "ui ux", "ux design", "ui design", "user experience", "user interface design"]),
    ("Figma", "Design", "technical", ["figma"]),
    ("Adobe Photoshop", "Design", "technical", ["photoshop", "adobe photoshop"]),
    ("Wireframing", "Design", "technical", ["wireframing", "wireframes", "prototyping"]),
    ("Graphic Design", "Design", "technical", ["graphic design", "canva", "adobe illustrator"]),
    ("Project Management", "Business & Management", "technical", ["project management", "pmp"]),
    ("Agile", "Business & Management", "technical", ["agile", "scrum", "kanban"]),
    ("Product Management", "Business & Management", "technical", ["product management", "product manager"]),
    ("Business Analysis", "Business & Management", "technical", ["business analysis", "requirements gathering", "business analyst"]),
    ("Digital Marketing", "Business & Management", "technical", ["digital marketing", "social media marketing", "google ads", "email marketing"]),
    ("SEO", "Business & Management", "technical", ["seo", "search engine optimization", "search engine optimisation"]),
    ("Content Writing", "Business & Management", "technical", ["content writing", "copywriting", "technical writing", "content creation"]),
    ("Communication", "Soft Skills", "non-technical", ["communication", "communication skills", "public speaking", "presentation skills"]),
    ("Leadership", "Soft Skills", "non-technical", ["leadership", "team lead", "led a team", "team management"]),
    ("Teamwork", "Soft Skills", "non-technical", ["teamwork", "team player", "collaboration", "collaborative"]),
    ("Problem Solving", "Soft Skills", "non-technical", ["problem solving", "problem-solving", "analytical thinking"]),
    ("Critical Thinking", "Soft Skills", "non-technical", ["critical thinking"]),
    ("Time Management", "Soft Skills", "non-technical", ["time management", "prioritization"]),
    ("Adaptability", "Soft Skills", "non-technical", ["adaptability", "adaptable", "quick learner", "fast learner"]),
    ("Creativity", "Soft Skills", "non-technical", ["creativity", "creative thinking", "innovative"]),
    ("Software Testing", "Quality Assurance", "technical", ["software testing", "manual testing", "test automation", "quality assurance", "unit testing", "pytest", "junit", "jest"]),
    ("Selenium", "Quality Assurance", "technical", ["selenium", "cypress"]),
]

TAXONOMY = {n: {"area": a, "type": t, "aliases": al} for n, a, t, al in _RAW}
LOWER = {n.lower(): n for n in TAXONOMY}
AREA_TIPS = {
    "Programming": "practice daily on a coding platform and build a small CLI or API project",
    "Web Development": "build and deploy a responsive full-stack app with authentication",
    "Data & AI": "complete a Kaggle-style project and publish the notebook with clear insights",
    "Cloud & DevOps": "containerise an app and deploy it with a CI/CD pipeline on a free cloud tier",
    "Databases": "design a normalised schema and write joins, indexes and transactions by hand",
    "Mobile": "ship a small app to an emulator or store with API integration",
    "Security & Networking": "work through hands-on labs (e.g. TryHackMe) and document what you learn",
    "Design": "create a case study with research, wireframes and a polished prototype",
    "Business & Management": "run or document a small project using real planning artefacts",
    "Soft Skills": "give concrete examples (STAR format) in your experience and project bullets",
    "Quality Assurance": "write an automated test suite for an open-source project",
}

_PATTERNS = {
    n: re.compile(r"(?<![A-Za-z0-9+#.])(?:%s)(?![A-Za-z0-9+#])" % "|".join(
        re.escape(a) for a in sorted(d["aliases"], key=len, reverse=True)))
    for n, d in TAXONOMY.items()
}


def find_skills(text: str) -> dict:
    """Return {canonical skill: number of mentions} found in text."""
    low = text.lower()
    out = {}
    for name, pat in _PATTERNS.items():
        c = len(pat.findall(low))
        if c:
            out[name] = c
    return out


def canonical(name: str) -> str:
    return LOWER.get(name.strip().lower(), name.strip())


def area_of(skill: str) -> str:
    return TAXONOMY.get(canonical(skill), {}).get("area", "General")


def suggestion_for(skill: str) -> str:
    area = area_of(skill)
    tip = AREA_TIPS.get(area, "build a small portfolio project that applies it end to end")
    return f"Take a structured course in {skill}, then {tip}; list the result on your resume."
