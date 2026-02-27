from typing import Optional, Dict, Any
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Simple in-memory user store for demo purposes
# In a production environment, this would be replaced by a robust database (e.g., PostgreSQL)
USERS: Dict[str, Dict[str, Any]] = {
    "admin@ecopulse.ai": {
        "id": "1",
        "username": "admin",
        "password": generate_password_hash("greenbharat2026"),
        "role": "city_admin",
    }
}


class User(UserMixin):
    """
    Representation of a system user for authentication and authorization.
    """

    def __init__(self, id: str, email: str, username: str, role: str):
        self.id = id
        self.email = email
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        """
        Retrieves a user instance by their unique identifier.

        Args:
            user_id (str): The unique ID of the user.

        Returns:
            Optional[User]: The User object if found, otherwise None.
        """
        for email, data in USERS.items():
            if data["id"] == user_id:
                return User(user_id, email, data["username"], data["role"])
        return None

    @staticmethod
    def find_by_email(email: str) -> Optional["User"]:
        """
        Retrieves a user instance by their email address.

        Args:
            email (str): The email address of the user.

        Returns:
            Optional[User]: The User object if found, otherwise None.
        """
        if email in USERS:
            data = USERS[email]
            return User(data["id"], email, data["username"], data["role"])
        return None

    def verify_password(self, password: str) -> bool:
        """
        Validates the provided password against the stored hash.

        Args:
            password (str): The plain-text password to verify.

        Returns:
            bool: True if password matches, False otherwise.
        """
        return check_password_hash(USERS[self.email]["password"], password)
