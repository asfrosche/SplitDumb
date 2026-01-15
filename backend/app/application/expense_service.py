"""
Application service for expense operations.
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.infrastructure.repositories.expense_repository import ExpenseRepository
from app.infrastructure.repositories.group_repository import GroupRepository
from app.infrastructure.repositories.activity_repository import ActivityRepository
from app.domain.expense_service import ExpenseService
from app.infrastructure.db.models import (
    Expense, ExpenseItem, ExpenseSplit, SplitType, ActivityEventType
)


class ExpenseServiceApp:
    """Application service for expense operations."""

    def __init__(self, db: Session):
        self.expense_repo = ExpenseRepository(db)
        self.group_repo = GroupRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.db = db

    def create_expense(
        self,
        group_id: int,
        payer_user_id: int,
        created_by_user_id: int,
        amount_cents: int,
        currency_code: str,
        description: str,
        notes: Optional[str] = None,
        category_id: Optional[int] = None,
        split_type: SplitType = SplitType.EQUAL,
        split_data: Dict = None,
        items: Optional[List[Dict]] = None,
    ) -> Expense:
        """Create a new expense with splits."""
        # Validate group membership
        if not self.group_repo.is_member(group_id, payer_user_id):
            raise ValueError("Payer must be a member of the group")

        # Create expense
        expense = Expense(
            group_id=group_id,
            payer_user_id=payer_user_id,
            created_by_user_id=created_by_user_id,
            amount_cents=amount_cents,
            currency_code=currency_code,
            description=description,
            notes=notes,
            category_id=category_id,
        )

        # Handle itemized expenses
        if items:
            # Create items and their splits
            total_items_cents = 0
            for item_data in items:
                item = ExpenseItem(
                    expense=expense,
                    description=item_data["description"],
                    amount_cents=item_data["amount_cents"],
                    category_id=item_data.get("category_id"),
                )
                expense.items.append(item)
                total_items_cents += item_data["amount_cents"]

            # Validate total matches
            if total_items_cents != amount_cents:
                raise ValueError(f"Items total ({total_items_cents}) does not match expense amount ({amount_cents})")

            # Create splits for each item
            for item in expense.items:
                item_splits = ExpenseService.create_item_splits(item, split_type, split_data)
                expense.splits.extend(item_splits)
        else:
            # Whole expense split
            splits = ExpenseService.create_expense_splits(expense, split_type, split_data)
            expense.splits = splits

        # Validate all participants are group members
        participant_ids = {s.user_id for s in expense.splits}
        for user_id in participant_ids:
            if not self.group_repo.is_member(group_id, user_id):
                raise ValueError(f"User {user_id} is not a member of the group")

        # Save expense
        expense = self.expense_repo.create(expense)

        # Create activity event
        activity_event = ActivityEvent(
            group_id=group_id,
            user_id=created_by_user_id,
            type=ActivityEventType.EXPENSE_CREATED,
            payload={"expense_id": expense.id, "description": description, "amount_cents": amount_cents},
        )
        self.activity_repo.create(activity_event)

        return expense

    def update_expense(
        self,
        expense_id: int,
        user_id: int,
        amount_cents: Optional[int] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        split_type: Optional[SplitType] = None,
        split_data: Optional[Dict] = None,
    ) -> Expense:
        """Update an existing expense."""
        expense = self.expense_repo.get_by_id(expense_id)
        if not expense:
            raise ValueError("Expense not found")

        # Check permissions
        if not self.group_repo.is_member(expense.group_id, user_id):
            raise ValueError("User is not a member of the group")

        # Update fields
        if amount_cents is not None:
            expense.amount_cents = amount_cents
        if description is not None:
            expense.description = description
        if notes is not None:
            expense.notes = notes

        # Update splits if provided
        if split_type and split_data:
            # Clear existing splits
            self.db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()

            # Create new splits
            if expense.items:
                for item in expense.items:
                    item_splits = ExpenseService.create_item_splits(item, split_type, split_data)
                    expense.splits.extend(item_splits)
            else:
                splits = ExpenseService.create_expense_splits(expense, split_type, split_data)
                expense.splits = splits

        expense = self.expense_repo.update(expense)

        # Create activity event
        activity_event = ActivityEvent(
            group_id=expense.group_id,
            user_id=user_id,
            type=ActivityEventType.EXPENSE_UPDATED,
            payload={"expense_id": expense.id},
        )
        self.activity_repo.create(activity_event)

        return expense

    def delete_expense(self, expense_id: int, user_id: int) -> None:
        """Soft delete an expense."""
        expense = self.expense_repo.get_by_id(expense_id)
        if not expense:
            raise ValueError("Expense not found")

        # Check permissions
        if not self.group_repo.is_member(expense.group_id, user_id):
            raise ValueError("User is not a member of the group")

        self.expense_repo.soft_delete(expense_id)

        # Create activity event
        activity_event = ActivityEvent(
            group_id=expense.group_id,
            user_id=user_id,
            type=ActivityEventType.EXPENSE_DELETED,
            payload={"expense_id": expense.id},
        )
        self.activity_repo.create(activity_event)

    def get_group_expenses(self, group_id: int, limit: int = 50, offset: int = 0) -> List[Expense]:
        """Get paginated expenses for a group."""
        return self.expense_repo.get_group_expenses(group_id, limit, offset)
