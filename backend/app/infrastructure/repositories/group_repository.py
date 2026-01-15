"""
Group repository for database operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.db.models import Group, GroupMember, User


class GroupRepository:
    """Repository for group operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID with members loaded."""
        return (
            self.db.query(Group)
            .options(joinedload(Group.members).joinedload(GroupMember.user))
            .filter(Group.id == group_id)
            .first()
        )

    def get_user_groups(self, user_id: int) -> List[Group]:
        """Get all groups a user belongs to."""
        return (
            self.db.query(Group)
            .join(GroupMember)
            .filter(GroupMember.user_id == user_id)
            .options(joinedload(Group.members).joinedload(GroupMember.user))
            .all()
        )

    def create(self, name: str, created_by_user_id: int, default_currency: str = "USD") -> Group:
        """Create a new group and add creator as owner."""
        group = Group(
            name=name,
            created_by_user_id=created_by_user_id,
            default_currency=default_currency,
        )
        self.db.add(group)
        self.db.flush()

        # Add creator as owner
        member = GroupMember(
            group_id=group.id,
            user_id=created_by_user_id,
            role="owner",
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(group)
        return group

    def add_member(self, group_id: int, user_id: int) -> GroupMember:
        """Add a user to a group."""
        member = GroupMember(group_id=group_id, user_id=user_id, role="member")
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def is_member(self, group_id: int, user_id: int) -> bool:
        """Check if user is a member of the group."""
        return (
            self.db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            .first()
            is not None
        )
