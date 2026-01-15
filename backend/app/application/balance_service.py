"""
Application service for balance operations.
"""
from typing import Dict
from sqlalchemy.orm import Session

from app.infrastructure.repositories.group_repository import GroupRepository
from app.infrastructure.repositories.expense_repository import ExpenseRepository
from app.infrastructure.repositories.settlement_repository import SettlementRepository
from app.domain.balance_service import BalanceService


class BalanceServiceApp:
    """Application service for balance operations."""

    def __init__(self, db: Session):
        self.group_repo = GroupRepository(db)
        self.expense_repo = ExpenseRepository(db)
        self.settlement_repo = SettlementRepository(db)
        self.db = db

    def get_group_balances(self, group_id: int, user_id: int) -> Dict:
        """Get balances for all users in a group."""
        # Validate membership
        if not self.group_repo.is_member(group_id, user_id):
            raise ValueError("User is not a member of this group")

        # Get expenses and settlements
        expenses = self.expense_repo.get_group_expenses(group_id, limit=1000)
        settlements = self.settlement_repo.get_group_settlements(group_id)

        # Calculate balances
        balances = BalanceService.calculate_group_balances(expenses, settlements)

        return {"balances": balances}
