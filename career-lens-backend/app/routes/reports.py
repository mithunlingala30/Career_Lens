from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from ..database import get_store
from ..services.report_service import build_report
from ..utils.security import require_candidate

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{evaluation_id}/pdf")
def pdf(evaluation_id: int, store=Depends(get_store), user: dict = Depends(require_candidate)):
    ev = store.get("resume_evaluations", evaluation_id)
    if not ev or ev["user_id"] != user["id"]:
        raise HTTPException(404, "Evaluation not found")
    profile = store.get("candidate_profiles", ev["resume_id"])
    recs = sorted(store.where("career_recommendations", resume_id=ev["resume_id"]), key=lambda r: r["rank"])
    return Response(build_report(ev, profile, recs), media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="careerlens-report-{evaluation_id}.pdf"'})
