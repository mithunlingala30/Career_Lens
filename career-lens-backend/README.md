# ⚙️ CareerLens Backend

> **FastAPI + Firebase Firestore REST API Service**

For the complete step-by-step setup and architecture guide, refer to the [Main README.md](../README.md).

---

## 🚀 Quick Start

```powershell
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Place your firebase-service-account.json in this directory

# 4. Initialize database (Admin user + default jobs)
python -m scripts.init_db

# 5. Start development server
uvicorn app.main:app --reload --port 8000
```

---

## 🔗 Key Links

* **API Root:** [http://localhost:8000/](http://localhost:8000/)
* **Swagger Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🧪 Testing

Run backend tests using the local JSON-based mock store (no Firebase connection required):

```powershell
python -m tests.test_workflow
```
