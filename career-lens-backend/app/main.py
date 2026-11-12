"""CareerLens API - run with:  uvicorn app.main:app --reload --port 8000"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS, DB_BACKEND, UPLOAD_DIR
from .database import init_store
from .routes import analysis, auth, dashboard, evaluation, jobs, matching, recommendations, reports, resumes, skill_gaps
from .services import reference
from .services.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    store = init_store()                      # connects to Firestore (raises a clear message if the key file is missing)
    seed(store)                               # admin account + sample jobs (only when missing)
    reference.get_reference()                 # warm the calibration cohort / hypothesis-test cache
    print(f"CareerLens ready - database backend: {DB_BACKEND}")
    yield


app = FastAPI(title="CareerLens API", version="2.0.0", lifespan=lifespan,
              description="Automated resume evaluation and career recommendation platform (Firebase Firestore)")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for r in (auth, resumes, analysis, jobs, evaluation, matching, recommendations, skill_gaps, dashboard, reports):
    app.include_router(r.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "CareerLens API is running",
        "docs": "/docs",
        "health": "/api/health",
        "version": "2.0.0",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "database": DB_BACKEND}
