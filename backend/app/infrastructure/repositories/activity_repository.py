"""
Activity repository for database operations.
"""
from typing import List
from sqlalchemy.orm import Session

from app.infrastructure.db.models import ActivityEvent


class ActivityRepository:
    """Repository for activity feed operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_group_activity(self, group_id: int, limit: int = 50, offset: int = 0) -> List[ActivityEvent]:
        """Get paginated activity events for a group."""
        return (
            self.db.query(ActivityEvent)
            .filter(ActivityEvent.group_id == group_id)
            .order_by(ActivityEvent.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def create(self, event: ActivityEvent) -> ActivityEvent:
        """Create a new activity event."""
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
