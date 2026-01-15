"""
Domain service for balance calculation.
Pure business logic for computing net balances per user per group per currency.
"""
from typing import Dict, List, Tuple
from collections import defaultdict

from app.infrastructure.db.models import Expense, ExpenseSplit, Settlement


class BalanceService:
    """
    Domain service for balance calculations.
    Computes net balances from expenses and settlements.
    """

    @staticmethod
    def calculate_group_balances(
        expenses: List[Expense],
        settlements: List[Settlement],
    ) -> Dict[str, Dict[int, int]]:
        """
        Calculate net balances per user per currency for a group.
        
        Returns: {
            currency_code: {
                user_id: balance_cents (positive = owed to user, negative = user owes)
            }
        }
        
        Logic:
        - For each expense split: user owes amount to payer
        - For each settlement: from_user pays to_user
        - Net balance = sum(amounts owed to user) - sum(amounts user owes)
        """
        balances: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

        # Process expenses
        for expense in expenses:
            if expense.deleted_at:
                continue

            currency = expense.currency_code
            payer_id = expense.payer_user_id

            # Payer is owed the total expense amount
            balances[currency][payer_id] += expense.amount_cents

            # Each split participant owes their share
            for split in expense.splits:
                user_id = split.user_id
                # User owes this amount (negative balance)
                balances[currency][user_id] -= split.amount_cents

        # Process settlements
        for settlement in settlements:
            currency = settlement.currency_code
            from_user_id = settlement.from_user_id
            to_user_id = settlement.to_user_id
            amount = settlement.amount_cents

            # from_user pays to_user
            balances[currency][from_user_id] -= amount
            balances[currency][to_user_id] += amount

        # Convert defaultdict to regular dict
        return {currency: dict(balances[currency]) for currency in balances}

    @staticmethod
    def get_user_balance_in_group(
        expenses: List[Expense],
        settlements: List[Settlement],
        user_id: int,
        currency_code: str,
    ) -> int:
        """
        Get net balance for a specific user in a group for a currency.
        Returns balance in cents (positive = owed to user, negative = user owes).
        """
        balances = BalanceService.calculate_group_balances(expenses, settlements)
        return balances.get(currency_code, {}).get(user_id, 0)

    @staticmethod
    def get_user_total_balance(
        expenses: List[Expense],
        settlements: List[Settlement],
        user_id: int,
    ) -> Dict[str, int]:
        """
        Get total balances for a user across all currencies.
        Returns: {currency_code: balance_cents}
        """
        balances = BalanceService.calculate_group_balances(expenses, settlements)
        return {currency: balances.get(currency, {}).get(user_id, 0) for currency in balances}
