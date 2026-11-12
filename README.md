# CareerLens - Automated Resume Evaluation and Career Recommendation Platform

React + Vite + Tailwind (neumorphic UI) · FastAPI · **Firebase Firestore** · NumPy / SciPy / scikit-learn · PyMuPDF · python-docx · ReportLab

Candidates register, upload a PDF/DOCX resume, review and correct the extracted profile, get a 0-100 resume score, job compatibility ranking, skill gaps,
career recommendations and a downloadable PDF report. Admins manage jobs, requirements and categories and see platform statistics.
Everything is stored in Firebase Firestore; resume files are stored in `career-lens-backend/uploads/resumes/` and their path is saved in Firestore. Data survives server restarts.

---
## 1. Windows setup (step by step)

### 1.1 Prerequisites
* **Python 3.10 - 3.12**: https://www.python.org/downloads/ (tick *Add python.exe to PATH*).
* **Node.js 18+ (LTS)**: https://nodejs.org/
* A free **Google account** for Firebase. No database software has to be installed.

### 1.2 Create the Firebase project and Firestore database
1. Open https://console.firebase.google.com → **Create a project** (or *Add project*) → name it e.g. `careerlens` → turn Google Analytics off → **Create**.
2. In the left menu choose **Build → Firestore Database → Create database**. Edition **Standard**, pick a nearby location (e.g. `asia-south1 (Mumbai)`; **the location cannot be changed later**), choose **Start in production mode**, then **Enable**.
3. Click the **gear icon → Project settings → Service accounts → Generate new private key → Generate key**. A `.json` file downloads.
4. Rename it to `firebase-service-account.json` and move it into `CareerLens\career-lens-backend\`.
   **Treat this file like a password** - never share it or upload it to GitHub (the `.gitignore` already excludes it).
5. (Recommended) Firestore Database → **Rules** tab → replace the text with the contents of `database\firestore.rules` → **Publish**. This blocks direct browser access; only your backend can touch the data.

The free *Spark* plan is enough: Firestore has a daily free quota and resume files are stored on your own computer in `uploads\resumes\`, so Firebase Storage (which needs a billing plan) is not used.

### 1.3 Backend  → http://localhost:8000  (Swagger: http://localhost:8000/docs)
```powershell
cd CareerLens\career-lens-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
```
In `.env` check `DB_BACKEND=firestore` and `FIREBASE_CREDENTIALS=firebase-service-account.json`, and change `SECRET_KEY` to a long random text. Then:
```powershell
python -m scripts.init_db        # connects to Firestore, creates the admin account and 15 sample jobs
uvicorn app.main:app --reload --port 8000
```
You should see `CareerLens ready - database backend: firestore`. If PowerShell blocks activation run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

### 1.4 Frontend  → http://localhost:5173
Open a second terminal:
```powershell
cd CareerLens\career-lens-frontend
npm install
copy .env.example .env           # VITE_API_URL=http://localhost:8000/api
npm run dev
```

### 1.5 Log in
* **Admin:** `admin@careerlens.com` / `Admin@123` (use the *Admin* tab on the login page; change it in `.env` before the first start).
* **Candidate:** click *Register*. Password rules: 8+ characters with upper-case, lower-case and a digit.
* Forgot password: no mail server is bundled, so in `DEBUG=true` the reset token is shown on screen; set `DEBUG=false` in production and plug in e-mail.

### 1.6 See your data in Firebase
Firebase console → **Firestore Database → Data**. Collections (`users`, `resumes`, `jobs`, `resume_evaluations`, ...) appear after the first run and fill as you use the site.

### 1.7 Try the whole workflow
Register → *Resume Upload* (drop a PDF/DOCX; extraction, job matching and career recommendations run automatically) → correct the extracted profile →
*Evaluation* (score, matched/missing skills, maths panel, Gaussian chart, hypothesis-test card, **PDF report**) → *Job Matching* → *Careers* → *Skill Gaps* → *History*.
Sign in as admin to add/edit/delete jobs, rename categories and view users and statistics.

Automated check of the backend flow: `cd career-lens-backend ; python -m tests.test_workflow` (uses a temporary local store, no Firebase needed).

---
## 2. Architecture
```
CareerLens/
├── career-lens-frontend/   React app (pages, components, layouts, services/api.js, context, hooks)
├── career-lens-backend/
│   ├── app/main.py database.py config.py
│   ├── app/database.py  Firestore store (+ local test store)   app/models/ document shapes   app/schemas/ request models
│   ├── app/routes/      REST endpoints            app/services/ parser, scoring, careers, reports, seed
│   ├── app/algorithms/  the 7 mathematical modules
│   ├── uploads/resumes/ uploaded files            scripts/ init_db    tests/
└── database/               FIRESTORE_COLLECTIONS.md (data model) and firestore.rules
```
Firestore collections: users, resumes, candidate_profiles (skills, education, experience, certifications and projects embedded), jobs (requirements embedded), resume_evaluations, job_matches, skill_gaps, career_recommendations, evaluation_history - see `database/FIRESTORE_COLLECTIONS.md`.
Uniqueness, ownership and range rules are enforced in the API; multi-document results are written in one Firestore batch.

API (all under `/api`, JWT bearer): `auth/{register,login,me,forgot-password,reset-password}` · `resumes` (upload, list, get, file, delete) · `analysis/extract/{id}`, `analysis/{id}` (GET/PUT) ·
`jobs` CRUD (+ `categories`, `extract-skills`) · `evaluation/{resume}/{job}`, `evaluation/{resume}`, `evaluation/history`, `evaluation/validation` · `matching/{id}` · `recommendations/{id}` · `skill-gaps/{id}` ·
`dashboard/{candidate,admin}` · `reports/{evaluation_id}/pdf`. Admin-only routes return 403 for candidates; candidates only see their own resumes.

---
## 3. The mathematics (all in `app/algorithms/`, all feeding real outputs)
| Module | File | Used for |
|---|---|---|
| Inner product | `inner_product.py` | candidate skill vector · job requirement vector → coverage, cosine (45 % of compatibility) |
| Bayes' theorem | `bayes_model.py` | posterior P(suitable \| skills, education, experience) with a prior and per-skill likelihood ratios |
| Conditional probability | `conditional_probability.py` | empirical P(suitable \| coverage bin, education met, experience met) from a calibration set, Laplace-smoothed |
| SVD | `svd_analysis.py` | rank-3 decomposition of the job×skill matrix; candidate folded into latent space → latent fit (15 %) and skill "families" |
| Gaussian distribution | `gaussian_analysis.py` | z-score, percentile, CI and Shapiro-Wilk check of the resume score against the cohort (platform scores once ≥ 20 resumes exist) |
| Markov chain | `markov_chain.py` | 5 readiness stages; transition matrix driven by readiness and missing skills; n-month distribution, expected months to next milestone via the fundamental matrix |
| Hypothesis testing | `hypothesis_testing.py` | paired t-test (Brier error) and McNemar test: proposed matcher vs keyword matching, shown on the Evaluation and Admin pages |

Compatibility = 0.45·skills + 0.10·education + 0.10·experience + 0.20·probability(mean of Bayes and conditional) + 0.15·latent(SVD).
Resume score (0-100) = contact 15 + education 15 + skills 25 + experience 20 + projects 10 + certifications 10 + summary 5.
Nothing is random at run time: the same resume always yields the same numbers.

### Assumptions and limitations (please read)
* **Validation data is simulated.** No real hiring outcomes exist, so `services/reference.py` generates a deterministic (seed 42) cohort of 400 labelled candidate-job cases with noisy resumes. The first 200 calibrate the conditional-probability table and the logistic calibration of both methods; the other 200 are used for the hypothesis tests. The significant result therefore shows the method works on this simulated population - it is not evidence about real recruiters. Replace the generator with real labelled data when available.
* The Bayes likelihoods (0.85/0.25), prior (0.35), the score weights and the Markov rates are documented, expert-set assumptions; naive Bayes assumes skills are independent (tempered by using at most 6 effective skills).
* The Gaussian reference is the simulated cohort until 20 real resumes are scored; Shapiro-Wilk p-values are reported and an empirical percentile is shown when normality is rejected.
* SVD quality grows with the number of jobs; with a small catalogue only a few latent factors exist.
* Resume parsing is rule-based (regex, section headings, a ~100-skill taxonomy in `skills_taxonomy.py`). Unusual layouts, multi-column PDFs or scanned images (no OCR) may extract imperfectly - that is why every field is editable and re-scoring is one click. Add skills to the taxonomy to widen detection.
* Scores support decisions; they do not replace human judgement.

## 4. Troubleshooting
* `Firebase service-account key not found` → the `.json` key is not in `career-lens-backend` or `FIREBASE_CREDENTIALS` in `.env` has the wrong name.
* `403 Cloud Firestore API has not been used` / `NOT_FOUND ... database (default) does not exist` → finish step 1.2 (Create database) in the Firebase console; wait a minute and retry.
* `PERMISSION_DENIED` → the key belongs to a different Firebase project than the one where you created the database.
* Slow first request → Firestore connections warm up; the first call can take a few seconds.
* Browser shows *Cannot reach the server* → backend not running on port 8000 or `VITE_API_URL` is wrong; restart `npm run dev` after editing `.env`.
* CORS error → add your frontend origin to `CORS_ORIGINS` in the backend `.env`.
* `pip install` fails building a package → use Python 3.10-3.12 and upgrade pip (`python -m pip install -U pip`).
#   C a r e e r _ L e n s  
 