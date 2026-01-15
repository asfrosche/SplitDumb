"""
Pydantic schemas for request/response validation.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.infrastructure.db.models import SplitType


# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str
    default_currency: str = "USD"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    default_currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


# Group schemas
class GroupCreate(BaseModel):
    name: str
    default_currency: str = "USD"


class GroupMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str
    joined_at: datetime
    user: UserResponse

    model_config = {"from_attributes": True}


class GroupResponse(BaseModel):
    id: int
    name: str
    created_by_user_id: int
    default_currency: str
    created_at: datetime
    members: List[GroupMemberResponse] = []

    model_config = {"from_attributes": True}


class GroupAddMember(BaseModel):
    email: EmailStr


class GroupWithBalancesResponse(BaseModel):
    group: GroupResponse
    balances: Dict[str, Dict[int, int]]  # currency -> user_id -> balance_cents
    user_balance: Dict[str, int]  # currency -> balance_cents


# Expense schemas
class ExpenseItemCreate(BaseModel):
    description: str
    amount_cents: int
    category_id: Optional[int] = None


class ExpenseSplitData(BaseModel):
    """Split data for different split types."""
    participants: Optional[List[int]] = None  # For EQUAL
    splits: Optional[List[Dict[str, int]]] = None  # For UNEQUAL: [{"user_id": int, "amount_cents": int}]
    shares: Optional[List[Dict[str, int]]] = None  # For SHARES: [{"user_id": int, "share_count": int}]
    percents: Optional[List[Dict[str, float]]] = None  # For PERCENT: [{"user_id": int, "percent": float}]


class ExpenseCreate(BaseModel):
    payer_id: int
    amount_cents: int
    currency_code: str
    description: str
    notes: Optional[str] = None
    category_id: Optional[int] = None
    split_mode: SplitType = SplitType.EQUAL
    split_data: ExpenseSplitData
    items: Optional[List[ExpenseItemCreate]] = None


class ExpenseSplitResponse(BaseModel):
    id: int
    user_id: int
    amount_cents: int
    share_type: str
    share_value: Optional[str] = None

    model_config = {"from_attributes": True}


class ExpenseItemResponse(BaseModel):
    id: int
    description: str
    amount_cents: int
    category_id: Optional[int] = None

    model_config = {"from_attributes": True}


class ExpenseResponse(BaseModel):
    id: int
    group_id: Optional[int]
    payer_user_id: int
    amount_cents: int
    currency_code: str
    description: str
    notes: Optional[str] = None
    category_id: Optional[int] = None
    occurred_at: datetime
    created_at: datetime
    splits: List[ExpenseSplitResponse] = []
    items: List[ExpenseItemResponse] = []
    payer: UserResponse

    model_config = {"from_attributes": True}


class ExpenseUpdate(BaseModel):
    amount_cents: Optional[int] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    split_mode: Optional[SplitType] = None
    split_data: Optional[ExpenseSplitData] = None


# Balance schemas
class BalanceResponse(BaseModel):
    balances: Dict[str, Dict[int, int]]  # currency -> user_id -> balance_cents


# Settlement schemas
class SettlementCreate(BaseModel):
    from_user_id: int
    to_user_id: int
    amount_cents: int
    currency_code: str
    notes: Optional[str] = None


class SettlementResponse(BaseModel):
    id: int
    group_id: int
    from_user_id: int
    to_user_id: int
    amount_cents: int
    currency_code: str
    created_by_user_id: int
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Activity schemas
class ActivityEventResponse(BaseModel):
    id: int
    group_id: Optional[int]
    user_id: int
    type: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime
    user: UserResponse

    model_config = {"from_attributes": True}
