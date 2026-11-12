"""
Firestore collections used by CareerLens (document shapes). Related data is embedded in the parent document,
which is the Firestore way of modelling what a relational database does with child tables.

users                  id, full_name, email(lower-case, unique), password_hash, role[candidate|admin], is_active, reset_token, reset_token_expires
resumes                id, user_id, original_filename, stored_filename, file_path, file_type[pdf|docx], file_size, file_hash, raw_text,
                       status[uploaded|extracted], candidate_name, resume_score
candidate_profiles     id (= resume id), resume_id, user_id, full_name, email, phone, location, summary, total_experience_years,
                       highest_education_level, is_edited,
                       skills[{skill_name, skill_type, evidence_weight, source}], education[...], experience[...], certifications[...], projects[...]
jobs                   id, title, company, category, location, employment_type, salary_range, description, min_education_level,
                       min_experience_years, is_active, created_by, requirements[{skill_name, importance 1-5, is_mandatory}]   (= jobs + job_requirements)
resume_evaluations     id (= resume*100000+job), user_id, resume_id, job_id, scores..., details{full evaluation, math outputs}
job_matches            id (= resume*100000+job), user_id, resume_id, job_id, compatibility, rank, matched_count, missing_count, details
skill_gaps             id (= resume*100000+job), resume_id, job_id, matched[], missing[{skill, importance, mandatory, suggestion}]
career_recommendations id (= resume*100000+rank), user_id, resume_id, category, rank, suitability, readiness, required/existing/missing skills,
                       learning_areas, progression{ladder, markov, suggestions}
evaluation_history     id, user_id, resume_id, evaluation_id, job_id, resume_name, event_type, title, scores
_counters              one document per collection holding the last integer id issued
"""
COLLECTIONS = ["users", "resumes", "candidate_profiles", "jobs", "resume_evaluations", "job_matches",
               "skill_gaps", "career_recommendations", "evaluation_history"]
