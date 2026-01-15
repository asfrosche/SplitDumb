"""
Group API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import (
    GroupCreate, GroupResponse, GroupAddMember, GroupWithBalancesResponse
)
from app.infrastructure.db.models import User
from app.application.group_service import GroupService

router = APIRouter()


@router.get("", response_model=List[GroupResponse])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all groups the current user belongs to."""
    group_service = GroupService(db)
    groups = group_service.get_user_groups(current_user.id)
    return [GroupResponse.model_validate(g) for g in groups]


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new group."""
    group_service = GroupService(db)
    try:
        group = group_service.create_group(
            name=group_data.name,
            created_by_user_id=current_user.id,
            default_currency=group_data.default_currency,
        )
        return GroupResponse.model_validate(group)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{group_id}", response_model=GroupWithBalancesResponse)
async def get_group(
    group_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get group details with balances."""
    group_service = GroupService(db)
    try:
        result = group_service.get_group_with_balances(group_id, current_user.id)
        return GroupWithBalancesResponse(
            group=GroupResponse.model_validate(result["group"]),
            balances=result["balances"],
            user_balance=result["user_balance"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{group_id}/members", response_model=GroupResponse)
async def add_group_member(
    member_data: GroupAddMember,
    group_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a member to a group."""
    group_service = GroupService(db)
    try:
        group = group_service.add_member(group_id, member_data.email, current_user.id)
        return GroupResponse.model_validate(group)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
