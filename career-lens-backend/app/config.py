import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_BACKEND = os.getenv("DB_BACKEND", "firestore").lower()          # "firestore" (default) or "local" (JSON file, for tests/demo only)
_cred = os.getenv("FIREBASE_CREDENTIALS", "firebase-service-account.json")
FIREBASE_CREDENTIALS = str(Path(_cred) if Path(_cred).is_absolute() else BASE_DIR / _cred)
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", str(BASE_DIR / "local_data" / "db.json"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads" / "resumes")))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
ADMIN_NAME = os.getenv("ADMIN_NAME", "CareerLens Admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@careerlens.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
