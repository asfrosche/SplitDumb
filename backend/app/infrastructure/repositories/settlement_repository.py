"""
Settlement repository for database operations.
"""
from typing import List
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Settlement


class SettlementRepository:
    """Repository for settlement operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_group_settlements(self, group_id: int) -> List[Settlement]:
        """Get all settlements for a group."""
        return (
            self.db.query(Settlement)
            .filter(Settlement.group_id == group_id)
            .order_by(Settlement.created_at.desc())
            .all()
        )

    def create(self, settlement: Settlement) -> Settlement:
        """Create a new settlement."""
        self.db.add(settlement)
        self.db.commit()
        self.db.refresh(settlement)
        return settlement
