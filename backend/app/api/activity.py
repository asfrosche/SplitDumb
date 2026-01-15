"""
Activity feed API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import ActivityEventResponse
from app.infrastructure.db.models import User
from app.infrastructure.repositories.activity_repository import ActivityRepository
from app.infrastructure.repositories.group_repository import GroupRepository

router = APIRouter()


@router.get("/{group_id}/activity", response_model=List[ActivityEventResponse])
async def get_group_activity(
    group_id: int = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated activity feed for a group."""
    group_repo = GroupRepository(db)
    if not group_repo.is_member(group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    activity_repo = ActivityRepository(db)
    events = activity_repo.get_group_activity(group_id, limit, offset)
    return [ActivityEventResponse.model_validate(e) for e in events]
