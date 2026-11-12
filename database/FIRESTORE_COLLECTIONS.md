# Firestore data model (replaces the PostgreSQL schema)

Firestore is a document database, so related child data is **embedded** in its parent document instead of living in separate tables.
Collections are created automatically on first write - there is nothing to run or migrate.

| Collection | Document id | Contents |
|---|---|---|
| `users` | auto integer | full_name, email (unique, lower-case), password_hash (bcrypt), role, is_active, reset token |
| `resumes` | auto integer | owner, original/stored filename, **file_path** (`uploads/resumes/...`), type, size, sha256 hash, raw_text, status, resume_score |
| `candidate_profiles` | = resume id | contact details, summary, experience years, education level, **skills[]**, **education[]**, **experience[]**, **certifications[]**, **projects[]** |
| `jobs` | auto integer | title, company, category, location, description, min education/experience, is_active, **requirements[]** (skill, importance 1-5, mandatory) |
| `resume_evaluations` | resume×100000+job | all scores + `details` (matched/missing skills, Bayes, conditional, inner product, SVD, Gaussian) |
| `job_matches` | resume×100000+job | compatibility, rank, matched/missing counts, details |
| `skill_gaps` | resume×100000+job | matched[] and missing[] skills with learning suggestions |
| `career_recommendations` | resume×100000+rank | category, suitability, readiness, skills, learning areas, progression + Markov forecast |
| `evaluation_history` | auto integer | permanent log of uploads, matches, evaluations, recommendations with their scores |
| `_counters` | collection name | last integer id issued (keeps ids numeric) |

Constraints that PostgreSQL enforced are enforced in the API code: unique e-mail, unique resume hash per user, unique job title+company,
importance 1-5, role values, ownership checks. Only equality queries are used, so **no composite indexes** are required.
Paste `firestore.rules` into Firebase console → Firestore → Rules and publish: it blocks all direct client access; only the backend (Admin SDK) can read or write.
