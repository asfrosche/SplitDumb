"""
Settlement API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import SettlementCreate, SettlementResponse
from app.infrastructure.db.models import User
from app.application.settlement_service import SettlementService

router = APIRouter()


@router.post("/{group_id}/settlements", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    settlement_data: SettlementCreate,
    group_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new settlement."""
    settlement_service = SettlementService(db)
    try:
        settlement = settlement_service.create_settlement(
            group_id=group_id,
            from_user_id=settlement_data.from_user_id,
            to_user_id=settlement_data.to_user_id,
            amount_cents=settlement_data.amount_cents,
            currency_code=settlement_data.currency_code,
            created_by_user_id=current_user.id,
            notes=settlement_data.notes,
        )
        return SettlementResponse.model_validate(settlement)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{group_id}/settlements", response_model=List[SettlementResponse])
async def list_settlements(
    group_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all settlements for a group."""
    settlement_service = SettlementService(db)
    try:
        settlements = settlement_service.get_group_settlements(group_id, current_user.id)
        return [SettlementResponse.model_validate(s) for s in settlements]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
