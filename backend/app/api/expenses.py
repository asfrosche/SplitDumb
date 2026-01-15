"""
Expense API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.api.schemas import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.infrastructure.db.models import User, SplitType
from app.application.expense_service import ExpenseServiceApp

router = APIRouter()


@router.get("/{group_id}/expenses", response_model=List[ExpenseResponse])
async def list_expenses(
    group_id: int = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated expenses for a group."""
    expense_service = ExpenseServiceApp(db)
    expenses = expense_service.get_group_expenses(group_id, limit, offset)
    return [ExpenseResponse.model_validate(e) for e in expenses]


@router.post("/{group_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    group_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new expense."""
    expense_service = ExpenseServiceApp(db)
    try:
        # Convert split_data to dict format expected by service
        split_data_dict = {}
        if expense_data.split_data.participants:
            split_data_dict["participants"] = expense_data.split_data.participants
        if expense_data.split_data.splits:
            split_data_dict["splits"] = expense_data.split_data.splits
        if expense_data.split_data.shares:
            split_data_dict["shares"] = expense_data.split_data.shares
        if expense_data.split_data.percents:
            split_data_dict["percents"] = expense_data.split_data.percents

        items_dict = None
        if expense_data.items:
            items_dict = [{"description": i.description, "amount_cents": i.amount_cents, "category_id": i.category_id} for i in expense_data.items]

        expense = expense_service.create_expense(
            group_id=group_id,
            payer_user_id=expense_data.payer_id,
            created_by_user_id=current_user.id,
            amount_cents=expense_data.amount_cents,
            currency_code=expense_data.currency_code,
            description=expense_data.description,
            notes=expense_data.notes,
            category_id=expense_data.category_id,
            split_type=expense_data.split_mode,
            split_data=split_data_dict,
            items=items_dict,
        )
        return ExpenseResponse.model_validate(expense)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_data: ExpenseUpdate,
    expense_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an expense."""
    expense_service = ExpenseServiceApp(db)
    try:
        split_data_dict = None
        if expense_data.split_data:
            if expense_data.split_data.participants:
                split_data_dict = {"participants": expense_data.split_data.participants}
            elif expense_data.split_data.splits:
                split_data_dict = {"splits": expense_data.split_data.splits}
            elif expense_data.split_data.shares:
                split_data_dict = {"shares": expense_data.split_data.shares}
            elif expense_data.split_data.percents:
                split_data_dict = {"percents": expense_data.split_data.percents}

        expense = expense_service.update_expense(
            expense_id=expense_id,
            user_id=current_user.id,
            amount_cents=expense_data.amount_cents,
            description=expense_data.description,
            notes=expense_data.notes,
            split_type=expense_data.split_mode,
            split_data=split_data_dict,
        )
        return ExpenseResponse.model_validate(expense)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an expense."""
    expense_service = ExpenseServiceApp(db)
    try:
        expense_service.delete_expense(expense_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
