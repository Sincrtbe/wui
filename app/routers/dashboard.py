"""Router de dashboard."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(channel_id: int | None = None, db: Session = Depends(get_db)):
    """Obtiene el resumen del dashboard."""
    return DashboardService.get_summary(db, channel_id)
