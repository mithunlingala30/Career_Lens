import hashlib
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..config import MAX_UPLOAD_MB, UPLOAD_DIR
from ..database import get_store
from ..services.analysis_service import log_history
from ..services.resume_parser import extract_text
from ..services.resume_service import resume_to_dict
from ..utils.helpers import newest_first, owned_resume
from ..utils.security import require_candidate

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...), store=Depends(get_store), user: dict = Depends(require_candidate)):
    name = file.filename or ""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(400, "Only PDF and DOCX resumes are supported")
    data = await file.read()
    if not data:
        raise HTTPException(400, "The uploaded file is empty")
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File is larger than {MAX_UPLOAD_MB} MB")
    digest = hashlib.sha256(data).hexdigest()
    if store.one("resumes", user_id=user["id"], file_hash=digest):
        raise HTTPException(409, "You already uploaded this exact resume")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored = f"u{user['id']}_{uuid.uuid4().hex}.{ext}"
    path = UPLOAD_DIR / stored
    path.write_bytes(data)
    try:
        text = extract_text(str(path), ext)
    except Exception:
        path.unlink(missing_ok=True)
        raise HTTPException(422, "Could not read this file - it may be corrupted or password protected")
    if len(text.strip()) < 30:
        path.unlink(missing_ok=True)
        raise HTTPException(422, "No readable text found (scanned image PDFs are not supported)")
    try:
        resume = store.create("resumes", {"user_id": user["id"], "original_filename": name[:255], "stored_filename": stored,
                                          "file_path": f"uploads/resumes/{stored}", "file_type": ext, "file_size": len(data), "file_hash": digest,
                                          "raw_text": text, "status": "uploaded", "candidate_name": "", "resume_score": None})
        log_history(resume, "upload", f"Uploaded {name}", {"file_type": ext, "size_kb": round(len(data) / 1024, 1)})
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return resume_to_dict(resume)


@router.get("")
def list_resumes(store=Depends(get_store), user: dict = Depends(require_candidate)):
    return [resume_to_dict(r) for r in newest_first(store.where("resumes", user_id=user["id"]))]


@router.get("/{resume_id}")
def get_resume(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    r = owned_resume(store, resume_id, user)
    return {**resume_to_dict(r), "raw_text": r["raw_text"]}


@router.get("/{resume_id}/file")
def download_file(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    r = owned_resume(store, resume_id, user)
    path = UPLOAD_DIR / r["stored_filename"]
    if not path.exists():
        raise HTTPException(404, "Stored file is missing from disk")
    mt = "application/pdf" if r["file_type"] == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(path, media_type=mt, filename=r["original_filename"])


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    r = owned_resume(store, resume_id, user)
    for col in ("job_matches", "skill_gaps", "career_recommendations", "resume_evaluations"):
        store.delete_where(col, resume_id=r["id"])
    for h in store.where("evaluation_history", resume_id=r["id"]):        # history survives so past scores stay viewable
        store.update("evaluation_history", h["id"], {"resume_id": None, "evaluation_id": None})
    store.delete("candidate_profiles", r["id"])
    store.delete("resumes", r["id"])
    (UPLOAD_DIR / r["stored_filename"]).unlink(missing_ok=True)
    return {"deleted": True}
