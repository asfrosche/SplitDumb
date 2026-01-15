"""
Expense repository for database operations.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.infrastructure.db.models import Expense, ExpenseSplit, ExpenseItem


class ExpenseRepository:
    """Repository for expense operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """Get expense by ID with splits and items loaded."""
        return (
            self.db.query(Expense)
            .options(
                joinedload(Expense.splits),
                joinedload(Expense.items).joinedload(ExpenseItem.splits),
            )
            .filter(Expense.id == expense_id, Expense.deleted_at.is_(None))
            .first()
        )

    def get_group_expenses(self, group_id: int, limit: int = 50, offset: int = 0) -> List[Expense]:
        """Get paginated expenses for a group."""
        return (
            self.db.query(Expense)
            .options(joinedload(Expense.splits), joinedload(Expense.payer))
            .filter(
                and_(Expense.group_id == group_id, Expense.deleted_at.is_(None))
            )
            .order_by(Expense.occurred_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def create(self, expense: Expense) -> Expense:
        """Create a new expense."""
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def update(self, expense: Expense) -> Expense:
        """Update an expense."""
        expense.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def soft_delete(self, expense_id: int) -> None:
        """Soft delete an expense."""
        expense = self.db.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            expense.deleted_at = datetime.utcnow()
            self.db.commit()
