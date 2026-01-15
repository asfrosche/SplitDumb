"""
Domain service for expense creation and split calculation.
Pure business logic, framework-agnostic.
"""
from typing import List, Dict
from decimal import Decimal, ROUND_HALF_UP

from app.infrastructure.db.models import Expense, ExpenseSplit, ExpenseItem, SplitType


class ExpenseService:
    """
    Domain service for expense operations.
    Handles split calculation and validation.
    """

    @staticmethod
    def calculate_equal_splits(
        amount_cents: int, participant_ids: List[int]
    ) -> List[Dict[str, int]]:
        """
        Calculate equal splits for participants.
        Returns list of {user_id, amount_cents} dicts.
        """
        if not participant_ids:
            raise ValueError("At least one participant required")

        per_person_cents = amount_cents // len(participant_ids)
        remainder = amount_cents % len(participant_ids)

        splits = []
        for i, user_id in enumerate(participant_ids):
            # Distribute remainder to first N participants
            amount = per_person_cents + (1 if i < remainder else 0)
            splits.append({"user_id": user_id, "amount_cents": amount})

        return splits

    @staticmethod
    def calculate_unequal_splits(
        amount_cents: int, splits: List[Dict[str, int]]
    ) -> List[Dict[str, int]]:
        """
        Validate and return unequal splits.
        splits: list of {user_id, amount_cents}
        """
        total = sum(s["amount_cents"] for s in splits)
        if total != amount_cents:
            raise ValueError(f"Split total ({total}) does not match expense amount ({amount_cents})")

        return splits

    @staticmethod
    def calculate_shares_splits(
        amount_cents: int, shares: List[Dict[str, int]]
    ) -> List[Dict[str, int]]:
        """
        Calculate splits based on share counts.
        shares: list of {user_id, share_count}
        Returns list of {user_id, amount_cents, share_value} dicts.
        """
        total_shares = sum(s["share_count"] for s in shares)
        if total_shares == 0:
            raise ValueError("Total shares must be greater than 0")

        result = []
        allocated = 0

        for i, share_data in enumerate(shares):
            user_id = share_data["user_id"]
            share_count = share_data["share_count"]

            # Calculate proportional amount
            if i == len(shares) - 1:
                # Last person gets remainder to avoid rounding errors
                amount = amount_cents - allocated
            else:
                # Calculate: (share_count / total_shares) * amount_cents
                amount_decimal = Decimal(share_count) / Decimal(total_shares) * Decimal(amount_cents)
                amount = int(amount_decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
                allocated += amount

            result.append({
                "user_id": user_id,
                "amount_cents": amount,
                "share_value": str(share_count),
            })

        return result

    @staticmethod
    def calculate_percent_splits(
        amount_cents: int, percents: List[Dict[str, float]]
    ) -> List[Dict[str, int]]:
        """
        Calculate splits based on percentages.
        percents: list of {user_id, percent}
        Returns list of {user_id, amount_cents, share_value} dicts.
        """
        total_percent = sum(p["percent"] for p in percents)
        if abs(total_percent - 100.0) > 0.01:  # Allow small floating point error
            raise ValueError(f"Percentages must sum to 100, got {total_percent}")

        result = []
        allocated = 0

        for i, percent_data in enumerate(percents):
            user_id = percent_data["user_id"]
            percent = percent_data["percent"]

            # Calculate proportional amount
            if i == len(percents) - 1:
                # Last person gets remainder to avoid rounding errors
                amount = amount_cents - allocated
            else:
                # Calculate: (percent / 100) * amount_cents
                amount_decimal = Decimal(percent) / Decimal(100) * Decimal(amount_cents)
                amount = int(amount_decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
                allocated += amount

            result.append({
                "user_id": user_id,
                "amount_cents": amount,
                "share_value": f"{percent}%",
            })

        return result

    @staticmethod
    def create_expense_splits(
        expense: Expense,
        split_type: SplitType,
        split_data: Dict,
    ) -> List[ExpenseSplit]:
        """
        Create ExpenseSplit objects for an expense based on split type and data.
        
        split_data structure depends on split_type:
        - EQUAL: {"participants": [user_id, ...]}
        - UNEQUAL: {"splits": [{"user_id": int, "amount_cents": int}, ...]}
        - SHARES: {"shares": [{"user_id": int, "share_count": int}, ...]}
        - PERCENT: {"percents": [{"user_id": int, "percent": float}, ...]}
        """
        amount_cents = expense.amount_cents
        splits = []

        if split_type == SplitType.EQUAL:
            participant_ids = split_data["participants"]
            calculated = ExpenseService.calculate_equal_splits(amount_cents, participant_ids)
            splits = [
                ExpenseSplit(
                    expense_id=expense.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.EQUAL,
                )
                for s in calculated
            ]

        elif split_type == SplitType.UNEQUAL:
            unequal_splits = split_data["splits"]
            calculated = ExpenseService.calculate_unequal_splits(amount_cents, unequal_splits)
            splits = [
                ExpenseSplit(
                    expense_id=expense.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.UNEQUAL,
                )
                for s in calculated
            ]

        elif split_type == SplitType.SHARES:
            shares = split_data["shares"]
            calculated = ExpenseService.calculate_shares_splits(amount_cents, shares)
            splits = [
                ExpenseSplit(
                    expense_id=expense.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.SHARES,
                    share_value=s.get("share_value"),
                )
                for s in calculated
            ]

        elif split_type == SplitType.PERCENT:
            percents = split_data["percents"]
            calculated = ExpenseService.calculate_percent_splits(amount_cents, percents)
            splits = [
                ExpenseSplit(
                    expense_id=expense.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.PERCENT,
                    share_value=s.get("share_value"),
                )
                for s in calculated
            ]

        return splits

    @staticmethod
    def create_item_splits(
        item: ExpenseItem,
        split_type: SplitType,
        split_data: Dict,
    ) -> List[ExpenseSplit]:
        """
        Create ExpenseSplit objects for an expense item.
        Same logic as create_expense_splits but for items.
        """
        amount_cents = item.amount_cents
        splits = []

        if split_type == SplitType.EQUAL:
            participant_ids = split_data["participants"]
            calculated = ExpenseService.calculate_equal_splits(amount_cents, participant_ids)
            splits = [
                ExpenseSplit(
                    expense_id=item.expense_id,
                    item_id=item.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.EQUAL,
                )
                for s in calculated
            ]

        elif split_type == SplitType.UNEQUAL:
            unequal_splits = split_data["splits"]
            calculated = ExpenseService.calculate_unequal_splits(amount_cents, unequal_splits)
            splits = [
                ExpenseSplit(
                    expense_id=item.expense_id,
                    item_id=item.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.UNEQUAL,
                )
                for s in calculated
            ]

        elif split_type == SplitType.SHARES:
            shares = split_data["shares"]
            calculated = ExpenseService.calculate_shares_splits(amount_cents, shares)
            splits = [
                ExpenseSplit(
                    expense_id=item.expense_id,
                    item_id=item.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.SHARES,
                    share_value=s.get("share_value"),
                )
                for s in calculated
            ]

        elif split_type == SplitType.PERCENT:
            percents = split_data["percents"]
            calculated = ExpenseService.calculate_percent_splits(amount_cents, percents)
            splits = [
                ExpenseSplit(
                    expense_id=item.expense_id,
                    item_id=item.id,
                    user_id=s["user_id"],
                    amount_cents=s["amount_cents"],
                    share_type=SplitType.PERCENT,
                    share_value=s.get("share_value"),
                )
                for s in calculated
            ]

        return splits
