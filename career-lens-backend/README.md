# CareerLens backend (FastAPI + Firebase Firestore)
See the root `README.md` for the complete Windows + Firebase setup. Quick start:
```
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          (put firebase-service-account.json in this folder)
python -m scripts.init_db
uvicorn app.main:app --reload --port 8000
```
Swagger: http://localhost:8000/docs · Tests: `python -m tests.test_workflow` (uses a throw-away local JSON store with the same interface as Firestore).
