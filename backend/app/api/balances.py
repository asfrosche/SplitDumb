"""
Balance API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import BalanceResponse
from app.infrastructure.db.models import User
from app.application.balance_service import BalanceServiceApp

router = APIRouter()


@router.get("/{group_id}/balances", response_model=BalanceResponse)
async def get_group_balances(
    group_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get balances for all users in a group."""
    balance_service = BalanceServiceApp(db)
    try:
        result = balance_service.get_group_balances(group_id, current_user.id)
        return BalanceResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
