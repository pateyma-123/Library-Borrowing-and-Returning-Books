"""
Permissions and Access Control Module for Library Management System.

This module manages user permissions and access control for library operations.
It provides role-based access control (RBAC) and permission checking.

Roles:
    ADMIN: Full system access
    LIBRARIAN: Manage books, process returns
    PATRON: Borrow and return books
    GUEST: Read-only access

Classes:
    Role: Enum of available roles
    Permission: Enum of available permissions
    User: User with assigned role and permissions
    AccessControl: Permission checker

Author: Library Management Team
Version: 1.0
"""

from enum import Enum
from typing import Set, Dict, List
from dataclasses import dataclass, field


class Role(Enum):
    """
    User roles in the library system.

    Roles:
        ADMIN: Administrator with full system access
        LIBRARIAN: Library staff member
        PATRON: Regular library user
        GUEST: Read-only visitor
    """
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    PATRON = "patron"
    GUEST = "guest"


class Permission(Enum):
    """
    Available permissions in the library system.

    Permissions:
        VIEW_BOOKS: View book inventory
        ADD_BOOK: Add new books
        REMOVE_BOOK: Remove books from inventory
        EDIT_BOOK: Modify book information
        BORROW_BOOK: Borrow books
        RETURN_BOOK: Return borrowed books
        VIEW_FINES: View fine amounts
        MANAGE_FINES: Create/modify fines
        VIEW_REPORTS: Access system reports
        MANAGE_USERS: Manage user accounts
        VIEW_LOGS: Access system logs
        EDIT_SETTINGS: Modify system settings
    """
    VIEW_BOOKS = "view_books"
    ADD_BOOK = "add_book"
    REMOVE_BOOK = "remove_book"
    EDIT_BOOK = "edit_book"
    BORROW_BOOK = "borrow_book"
    RETURN_BOOK = "return_book"
    VIEW_FINES = "view_fines"
    MANAGE_FINES = "manage_fines"
    VIEW_REPORTS = "view_reports"
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    EDIT_SETTINGS = "edit_settings"


@dataclass
class User:
    """
    Represents a library system user with role and permissions.

    Attributes:
        user_id (str): Unique user identifier
        name (str): User's full name
        role (Role): User's role in the system
        permissions (Set[Permission]): Explicit permissions granted
        is_active (bool): Whether user account is active
    """
    user_id: str
    name: str
    role: Role = Role.GUEST
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True

    def has_permission(self, permission: Permission) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission (Permission): Permission to check

        Returns:
            bool: True if user has permission, False otherwise
        """
        if not self.is_active:
            return False

        # Check explicit permissions
        if permission in self.permissions:
            return True

        # Check role-based permissions
        role_permissions = ROLE_PERMISSIONS.get(self.role, set())
        return permission in role_permissions

    def add_permission(self, permission: Permission) -> None:
        """
        Grant explicit permission to user.

        Args:
            permission (Permission): Permission to grant
        """
        self.permissions.add(permission)

    def remove_permission(self, permission: Permission) -> None:
        """
        Revoke explicit permission from user.

        Args:
            permission (Permission): Permission to revoke
        """
        self.permissions.discard(permission)

    def change_role(self, new_role: Role) -> None:
        """
        Change user's role.

        Args:
            new_role (Role): New role to assign
        """
        self.role = new_role


class AccessControl:
    """
    Permission checking and access control system.

    Provides methods to check user permissions and enforce access control
    throughout the library system.
    """

    def __init__(self):
        """
        Initialize access control system.
        """
        self.users: Dict[str, User] = {}

    def create_user(self, user_id: str, name: str, role: Role = Role.GUEST) -> User:
        """
        Create a new user account.

        Args:
            user_id (str): Unique user identifier
            name (str): User's full name
            role (Role): User's role (default: GUEST)

        Returns:
            User: Created user object
        """
        user = User(user_id=user_id, name=name, role=role)
        self.users[user_id] = user
        return user

    def get_user(self, user_id: str) -> User:
        """
        Retrieve user by ID.

        Args:
            user_id (str): User identifier

        Returns:
            User: User object or None if not found
        """
        return self.users.get(user_id)

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if user has permission to perform action.

        Args:
            user_id (str): User identifier
            permission (Permission): Permission to check

        Returns:
            bool: True if user has permission, False otherwise
        """
        user = self.get_user(user_id)
        if user is None:
            return False
        return user.has_permission(permission)

    def check_permission_bulk(self, user_id: str, 
                             permissions: List[Permission]) -> bool:
        """
        Check if user has ALL specified permissions.

        Args:
            user_id (str): User identifier
            permissions (List[Permission]): Permissions to check

        Returns:
            bool: True if user has ALL permissions, False otherwise
        """
        user = self.get_user(user_id)
        if user is None:
            return False
        return all(user.has_permission(p) for p in permissions)

    def enforce_permission(self, user_id: str, permission: Permission) -> None:
        """
        Enforce permission check, raise exception if denied.

        Args:
            user_id (str): User identifier
            permission (Permission): Permission required

        Raises:
            PermissionError: If user doesn't have permission
        """
        if not self.check_permission(user_id, permission):
            raise PermissionError(
                f"User {user_id} does not have permission: {permission.value}"
            )

    def list_users(self) -> List[User]:
        """
        List all registered users.

        Returns:
            List[User]: List of all users
        """
        return list(self.users.values())

    def get_user_count(self) -> int:
        """
        Get total count of registered users.

        Returns:
            int: Number of users
        """
        return len(self.users)

    def get_users_by_role(self, role: Role) -> List[User]:
        """
        Get all users with a specific role.

        Args:
            role (Role): Role to filter by

        Returns:
            List[User]: Users with specified role
        """
        return [u for u in self.users.values() if u.role == role]


# ===================== Role-Permission Mapping =====================

ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.VIEW_BOOKS,
        Permission.ADD_BOOK,
        Permission.REMOVE_BOOK,
        Permission.EDIT_BOOK,
        Permission.BORROW_BOOK,
        Permission.RETURN_BOOK,
        Permission.VIEW_FINES,
        Permission.MANAGE_FINES,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_USERS,
        Permission.VIEW_LOGS,
        Permission.EDIT_SETTINGS,
    },
    Role.LIBRARIAN: {
        Permission.VIEW_BOOKS,
        Permission.ADD_BOOK,
        Permission.REMOVE_BOOK,
        Permission.EDIT_BOOK,
        Permission.RETURN_BOOK,
        Permission.VIEW_FINES,
        Permission.MANAGE_FINES,
        Permission.VIEW_REPORTS,
        Permission.VIEW_LOGS,
    },
    Role.PATRON: {
        Permission.VIEW_BOOKS,
        Permission.BORROW_BOOK,
        Permission.RETURN_BOOK,
        Permission.VIEW_FINES,
    },
    Role.GUEST: {
        Permission.VIEW_BOOKS,
    }
}


def get_role_permissions(role: Role) -> Set[Permission]:
    """
    Get all permissions for a role.

    Args:
        role (Role): Role to get permissions for

    Returns:
        Set[Permission]: All permissions for the role
    """
    return ROLE_PERMISSIONS.get(role, set())
