from fastapi import APIRouter, Depends

from app.services.deps import get_summary_service
from app.services.summary_service import SummaryService
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.summary import SummaryResponse, SummaryQueryParams

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/", response_model=SummaryResponse)
def get_financial_summary(
    params: SummaryQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    summary_service: SummaryService = Depends(get_summary_service)
):
    return summary_service.get_user_summary(
        user_id=current_user.id,
        params=params
    )
