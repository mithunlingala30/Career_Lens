"""Sample career categories / job descriptions and the admin account (idempotent)."""
from ..config import ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD
from ..utils.security import hash_password
from .skills_taxonomy import canonical


def J(title, company, category, location, edu, exp, salary, desc, reqs, mandatory=()):
    return {"title": title, "company": company, "category": category, "location": location, "min_education_level": edu,
            "min_experience_years": exp, "salary_range": salary, "description": desc,
            "requirements": [(k.split(":")[0], int(k.split(":")[1])) for k in reqs.split(",")], "mandatory": set(mandatory)}


SEED_JOBS = [
    J("Full Stack Developer", "NovaStack Labs", "Software Development", "Bengaluru", 2, 1, "6-12 LPA",
      "Build responsive web applications with React and Node.js. You must be strong in JavaScript and REST APIs, and comfortable with MongoDB and Git workflows.",
      "React:5,JavaScript:5,Node.js:4,REST APIs:4,HTML:3,CSS:3,MongoDB:3,Git:3,TypeScript:2", ("React", "JavaScript")),
    J("Backend Python Developer", "CloudNest", "Software Development", "Coimbatore", 2, 1, "6-11 LPA",
      "Design scalable APIs with Python and FastAPI or Django. Required: PostgreSQL, SQL, Docker. Unit testing and Git are a plus.",
      "Python:5,FastAPI:4,Django:3,PostgreSQL:4,SQL:4,Docker:3,REST APIs:4,Git:3,Software Testing:2", ("Python", "SQL")),
    J("Java Developer", "Finverse Systems", "Software Development", "Chennai", 2, 2, "6-14 LPA",
      "Develop enterprise microservices using Java and Spring Boot with MySQL. Strong problem solving and REST APIs knowledge required.",
      "Java:5,Spring Boot:5,SQL:4,MySQL:3,REST APIs:4,Git:3,Microservices:3,Problem Solving:3", ("Java",)),
    J("Data Analyst", "InsightWorks", "Data & AI", "Pune", 2, 0, "4-8 LPA",
      "Turn raw data into decisions. Must know SQL and Excel; Power BI or Tableau dashboards, data analysis and statistics are expected along with clear communication.",
      "SQL:5,Excel:4,Power BI:4,Tableau:3,Data Analysis:5,Statistics:3,Data Visualization:4,Python:3,Communication:3", ("SQL",)),
    J("Data Scientist", "Quantiva AI", "Data & AI", "Hyderabad", 3, 1, "10-20 LPA",
      "Build predictive models with Python, Pandas, NumPy and Scikit-learn. Strong statistics and machine learning fundamentals required; SQL and deep learning are valuable.",
      "Python:5,Machine Learning:5,Statistics:5,Pandas:4,NumPy:4,Scikit-learn:4,Data Visualization:3,SQL:3,Deep Learning:3", ("Python", "Machine Learning")),
    J("Machine Learning Engineer", "NeuralForge", "Data & AI", "Bengaluru", 2, 2, "12-24 LPA",
      "Train and deploy deep learning models using TensorFlow or PyTorch. Docker and AWS experience preferred, NLP is a plus.",
      "Python:5,Machine Learning:5,Deep Learning:4,TensorFlow:4,PyTorch:4,Docker:3,AWS:3,NLP:3,Git:2", ("Python",)),
    J("DevOps Engineer", "InfraPulse", "Cloud & DevOps", "Chennai", 2, 2, "8-18 LPA",
      "Own CI/CD pipelines and container platforms. Must know Docker, Kubernetes and Linux; AWS, Jenkins and Terraform experience required.",
      "Docker:5,Kubernetes:5,CI/CD:4,Jenkins:3,AWS:4,Linux:4,Terraform:3,Git:3,Python:2", ("Docker",)),
    J("Cloud Engineer", "SkyBridge", "Cloud & DevOps", "Remote", 2, 1, "7-15 LPA",
      "Design secure cloud infrastructure on AWS and Azure. Linux, networking, Docker and Terraform knowledge expected.",
      "AWS:5,Azure:3,Linux:4,Docker:3,Terraform:3,Networking:3,Cybersecurity:2,Python:2", ("AWS",)),
    J("UI/UX Designer", "PixelCraft Studio", "Design", "Kochi", 2, 0, "4-9 LPA",
      "Create research-driven interfaces. Must be fluent in Figma and UI/UX design, wireframing and prototyping; creativity and communication essential.",
      "Figma:5,UI/UX Design:5,Wireframing:4,Adobe Photoshop:3,HTML:2,CSS:2,Creativity:3,Communication:3", ("Figma",)),
    J("Project Manager", "Orbit Consulting", "Business & Management", "Mumbai", 2, 4, "12-22 LPA",
      "Lead cross-functional teams using Agile and Scrum. Required: project management, strong leadership and communication; business analysis is a plus.",
      "Project Management:5,Agile:5,Leadership:5,Communication:4,Time Management:3,Business Analysis:3,Problem Solving:3", ("Project Management",)),
    J("Business Analyst", "Brightline Corp", "Business & Management", "Gurugram", 2, 1, "6-12 LPA",
      "Bridge business and technology teams through requirements gathering and business analysis. SQL, Excel, Power BI and Agile knowledge required.",
      "Business Analysis:5,SQL:3,Excel:4,Communication:4,Critical Thinking:3,Power BI:3,Agile:3", ("Business Analysis",)),
    J("Digital Marketing Specialist", "GrowthLoop", "Marketing", "Remote", 2, 1, "4-9 LPA",
      "Plan SEO and digital marketing campaigns, write engaging content and report performance using data analysis. Creativity and communication required.",
      "Digital Marketing:5,SEO:5,Content Writing:4,Communication:3,Creativity:3,Data Analysis:2", ("SEO",)),
    J("Mobile App Developer", "AppForge", "Mobile Development", "Bengaluru", 2, 1, "6-13 LPA",
      "Build Android and Flutter applications with Kotlin or Java. REST APIs, Firebase and Git skills required.",
      "Android:5,Flutter:4,Kotlin:4,Java:3,REST APIs:3,Git:3,Firebase:2", ("Android",)),
    J("QA Automation Engineer", "TestPilot", "Quality Assurance", "Coimbatore", 2, 1, "5-10 LPA",
      "Create automated test suites with Selenium and software testing frameworks. Python or Java scripting, Agile ways of working and CI/CD exposure required.",
      "Software Testing:5,Selenium:5,Python:3,Java:3,Agile:3,CI/CD:2,SQL:2", ("Selenium",)),
    J("Cybersecurity Analyst", "ShieldOps", "Cybersecurity", "Hyderabad", 2, 1, "7-15 LPA",
      "Monitor and defend enterprise networks. Must understand cybersecurity, networking and Linux; penetration testing and Python scripting valued.",
      "Cybersecurity:5,Networking:5,Linux:4,Penetration Testing:4,Python:2,Problem Solving:3", ("Cybersecurity",)),
]

CAREER_LADDERS = {
    "Software Development": ["Trainee Engineer", "Software Engineer", "Senior Engineer", "Tech Lead / Architect"],
    "Data & AI": ["Junior Analyst", "Data Scientist / Analyst", "Senior Data Scientist", "Principal / Head of Data"],
    "Cloud & DevOps": ["Junior Ops Engineer", "DevOps / Cloud Engineer", "Senior SRE", "Platform Architect"],
    "Design": ["Junior Designer", "UI/UX Designer", "Senior Designer", "Design Lead"],
    "Business & Management": ["Associate Analyst", "Business Analyst / Coordinator", "Project Manager", "Program Director"],
    "Marketing": ["Marketing Executive", "Digital Marketing Specialist", "Marketing Manager", "Head of Growth"],
    "Mobile Development": ["Junior App Developer", "Mobile Developer", "Senior Mobile Engineer", "Mobile Architect"],
    "Quality Assurance": ["QA Trainee", "QA Engineer", "Senior SDET", "QA Manager"],
    "Cybersecurity": ["SOC Trainee", "Security Analyst", "Security Engineer", "CISO Track"],
}


def seed(store):
    """Create the admin account and the sample jobs when they do not exist yet (idempotent)."""
    admin = store.one("users", role="admin")
    if not admin:
        admin = store.create("users", {"full_name": ADMIN_NAME, "email": ADMIN_EMAIL.lower(), "password_hash": hash_password(ADMIN_PASSWORD),
                                       "role": "admin", "is_active": True, "reset_token": None, "reset_token_expires": None})
    if not store.all("jobs"):
        for j in SEED_JOBS:
            store.create("jobs", {"title": j["title"], "company": j["company"], "category": j["category"], "location": j["location"],
                                  "employment_type": "Full-time", "salary_range": j["salary_range"], "description": j["description"],
                                  "min_education_level": j["min_education_level"], "min_experience_years": j["min_experience_years"],
                                  "is_active": True, "created_by": admin["id"],
                                  "requirements": [{"skill_name": canonical(s), "importance": i, "is_mandatory": s in j["mandatory"]}
                                                   for s, i in j["requirements"]]})
