from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Simple in-memory user store for demo
# In a real app, this would be a database
USERS = {
    "admin@ecopulse.ai": {
        "id": "1",
        "username": "admin",
        "password": generate_password_hash("greenbharat2026"),
        "role": "city_admin"
    }
}

class User(UserMixin):
    def __init__(self, id, email, username, role):
        self.id = id
        self.email = email
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id):
        for email, data in USERS.items():
            if data['id'] == user_id:
                return User(user_id, email, data['username'], data['role'])
        return None

    @staticmethod
    def find_by_email(email):
        if email in USERS:
            data = USERS[email]
            return User(data['id'], email, data['username'], data['role'])
        return None

    def verify_password(self, password):
        return check_password_hash(USERS[self.email]['password'], password)
