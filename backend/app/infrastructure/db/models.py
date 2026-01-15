"""
SQLAlchemy database models for SplitDumb.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, BigInteger, ForeignKey, DateTime, Boolean, Enum as SQLEnum, JSON, Text
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class Currency(Base):
    """Currency lookup table."""
    __tablename__ = "currencies"

    code = Column(String(3), primary_key=True)  # ISO 4217 code (USD, EUR, etc.)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False)
    precision = Column(Integer, default=2)  # Decimal places (typically 2)


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    default_currency = Column(String(3), ForeignKey("currencies.code"), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    groups = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    expenses_paid = relationship("Expense", foreign_keys="Expense.payer_user_id", back_populates="payer")
    splits_owed = relationship("ExpenseSplit", back_populates="user")
    settlements_sent = relationship("Settlement", foreign_keys="Settlement.from_user_id", back_populates="from_user")
    settlements_received = relationship("Settlement", foreign_keys="Settlement.to_user_id", back_populates="to_user")
    activity_events = relationship("ActivityEvent", back_populates="user")


class Group(Base):
    """Group model for expense sharing."""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    default_currency = Column(String(3), ForeignKey("currencies.code"), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="group")
    activity_events = relationship("ActivityEvent", back_populates="group")


class GroupMemberRole(str, enum.Enum):
    """Group member role."""
    OWNER = "owner"
    MEMBER = "member"


class GroupMember(Base):
    """Group membership model."""
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(GroupMemberRole), default=GroupMemberRole.MEMBER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="groups")


class ExpenseType(str, enum.Enum):
    """Expense type: group expense or personal expense (for future budgeting)."""
    GROUP = "group"
    PERSONAL = "personal"


class ExpenseSource(str, enum.Enum):
    """Expense source: manual entry now, bank import later."""
    MANUAL = "manual"
    BANK = "bank"


class Expense(Base):
    """Expense model."""
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # Nullable for personal expenses
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payer_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_cents = Column(BigInteger, nullable=False)  # Integer representation of money
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    description = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Optional for P0
    expense_type = Column(SQLEnum(ExpenseType), default=ExpenseType.GROUP)
    source = Column(SQLEnum(ExpenseSource), default=ExpenseSource.MANUAL)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", foreign_keys=[payer_user_id], back_populates="expenses_paid")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")
    items = relationship("ExpenseItem", back_populates="expense", cascade="all, delete-orphan")
    category = relationship("Category", back_populates="expenses")


class ExpenseItem(Base):
    """Optional per-item breakdown for expenses."""
    __tablename__ = "expense_items"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    description = Column(String(500), nullable=False)
    amount_cents = Column(BigInteger, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relationships
    expense = relationship("Expense", back_populates="items")
    splits = relationship("ExpenseSplit", back_populates="item")
    category = relationship("Category", back_populates="expense_items")


class SplitType(str, enum.Enum):
    """Split calculation type."""
    EQUAL = "equal"
    UNEQUAL = "unequal"
    SHARES = "shares"
    PERCENT = "percent"


class ExpenseSplit(Base):
    """Represents how much each participant owes for an expense (or item)."""
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("expense_items.id"), nullable=True)  # Null for whole-expense splits
    amount_cents = Column(BigInteger, nullable=False)  # Amount this user owes
    share_type = Column(SQLEnum(SplitType), nullable=False)
    share_value = Column(String(50), nullable=True)  # e.g., share count or percent for auditing

    # Relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="splits_owed")
    item = relationship("ExpenseItem", back_populates="splits")


class Settlement(Base):
    """Manual settle-up payment between users within a group."""
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_cents = Column(BigInteger, nullable=False)
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    group = relationship("Group", back_populates="settlements")
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="settlements_sent")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="settlements_received")


class ActivityEventType(str, enum.Enum):
    """Activity event types."""
    EXPENSE_CREATED = "expense_created"
    EXPENSE_UPDATED = "expense_updated"
    EXPENSE_DELETED = "expense_deleted"
    SETTLEMENT_CREATED = "settlement_created"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"


class ActivityEvent(Base):
    """Generic activity feed event for timeline/history."""
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # Nullable for user-level events
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(ActivityEventType), nullable=False)
    payload = Column(JSON, nullable=True)  # Flexible JSON for event-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    group = relationship("Group", back_populates="activity_events")
    user = relationship("User", back_populates="activity_events")


class Category(Base):
    """Expense category (optional in P0, placeholder for budgeting features)."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), nullable=True)  # Hex color code
    icon = Column(String(50), nullable=True)  # Icon identifier
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Personal category
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # Group-scoped category

    # Relationships
    expenses = relationship("Expense", back_populates="category")
    expense_items = relationship("ExpenseItem", back_populates="category")
