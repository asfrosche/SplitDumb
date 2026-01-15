"""
Application service for settlement operations.
"""
from typing import List
from sqlalchemy.orm import Session

from app.infrastructure.repositories.settlement_repository import SettlementRepository
from app.infrastructure.repositories.group_repository import GroupRepository
from app.infrastructure.repositories.activity_repository import ActivityRepository
from app.infrastructure.db.models import Settlement, ActivityEventType


class SettlementService:
    """Application service for settlement operations."""

    def __init__(self, db: Session):
        self.settlement_repo = SettlementRepository(db)
        self.group_repo = GroupRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.db = db

    def create_settlement(
        self,
        group_id: int,
        from_user_id: int,
        to_user_id: int,
        amount_cents: int,
        currency_code: str,
        created_by_user_id: int,
        notes: str = None,
    ) -> Settlement:
        """Create a new settlement."""
        # Validate group membership
        if not self.group_repo.is_member(group_id, from_user_id):
            raise ValueError("From user must be a member of the group")
        if not self.group_repo.is_member(group_id, to_user_id):
            raise ValueError("To user must be a member of the group")

        if from_user_id == to_user_id:
            raise ValueError("Cannot settle with yourself")

        # Create settlement
        settlement = Settlement(
            group_id=group_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            amount_cents=amount_cents,
            currency_code=currency_code,
            created_by_user_id=created_by_user_id,
            notes=notes,
        )

        settlement = self.settlement_repo.create(settlement)

        # Create activity event
        activity_event = ActivityEvent(
            group_id=group_id,
            user_id=created_by_user_id,
            type=ActivityEventType.SETTLEMENT_CREATED,
            payload={
                "settlement_id": settlement.id,
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "amount_cents": amount_cents,
            },
        )
        self.activity_repo.create(activity_event)

        return settlement

    def get_group_settlements(self, group_id: int, user_id: int) -> List[Settlement]:
        """Get all settlements for a group."""
        if not self.group_repo.is_member(group_id, user_id):
            raise ValueError("User is not a member of this group")

        return self.settlement_repo.get_group_settlements(group_id)
