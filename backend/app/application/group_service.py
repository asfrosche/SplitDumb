"""
Application service for group operations.
"""
from typing import List
from sqlalchemy.orm import Session

from app.infrastructure.repositories.group_repository import GroupRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.expense_repository import ExpenseRepository
from app.infrastructure.repositories.settlement_repository import SettlementRepository
from app.domain.balance_service import BalanceService
from app.infrastructure.db.models import Group


class GroupService:
    """Application service for group operations."""

    def __init__(self, db: Session):
        self.group_repo = GroupRepository(db)
        self.user_repo = UserRepository(db)
        self.expense_repo = ExpenseRepository(db)
        self.settlement_repo = SettlementRepository(db)
        self.db = db

    def get_user_groups(self, user_id: int) -> List[Group]:
        """Get all groups a user belongs to."""
        return self.group_repo.get_user_groups(user_id)

    def get_group_with_balances(self, group_id: int, user_id: int) -> dict:
        """Get group details with balance summary for the requesting user."""
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise ValueError("Group not found")

        if not self.group_repo.is_member(group_id, user_id):
            raise ValueError("User is not a member of this group")

        # Get expenses and settlements for balance calculation
        expenses = self.expense_repo.get_group_expenses(group_id, limit=1000)  # Get all for balance calc
        settlements = self.settlement_repo.get_group_settlements(group_id)

        # Calculate balances
        balances = BalanceService.calculate_group_balances(expenses, settlements)

        # Get user's balance summary
        user_balance_summary = {}
        for currency, user_balances in balances.items():
            user_balance_summary[currency] = user_balances.get(user_id, 0)

        return {
            "group": group,
            "balances": balances,
            "user_balance": user_balance_summary,
        }

    def create_group(self, name: str, created_by_user_id: int, default_currency: str = "USD") -> Group:
        """Create a new group."""
        return self.group_repo.create(name, created_by_user_id, default_currency)

    def add_member(self, group_id: int, user_email: str, added_by_user_id: int) -> Group:
        """Add a user to a group by email."""
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise ValueError("Group not found")

        # Check permissions (owner or member can add)
        if not self.group_repo.is_member(group_id, added_by_user_id):
            raise ValueError("User is not a member of this group")

        # Find user by email
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise ValueError("User not found")

        # Check if already a member
        if self.group_repo.is_member(group_id, user.id):
            raise ValueError("User is already a member of this group")

        # Add member
        self.group_repo.add_member(group_id, user.id)
        return self.group_repo.get_by_id(group_id)
