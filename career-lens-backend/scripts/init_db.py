"""Connect to Firestore and load the admin account + sample jobs.   Usage (from career-lens-backend/):  python -m scripts.init_db"""
from app.database import init_store
from app.services.seed import seed

if __name__ == "__main__":
    store = init_store()
    seed(store)
    print(f"Database ready: {len(store.all('jobs'))} jobs, admin account present.")
