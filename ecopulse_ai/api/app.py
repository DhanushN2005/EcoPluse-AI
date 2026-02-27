"""
EcoPulse AI Presentation Layer Factory.
Responsible for initializing the Flask application, configuring authentication,
and registering tactical routing blueprints.
"""

import os
import logging
from typing import Optional
from flask import Flask
from flask_login import LoginManager
from .models import User

# Configure module-level logging
logger = logging.getLogger("API-Application")


def create_app() -> Flask:
    """
    Application factory for constructing the Flask instance.
    Handles static/template path resolution, security keys, and user authentication.

    Returns:
        Flask: The configured Flask application instance.
    """
    # Automated path resolution for deployment flexibility
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(package_root, "templates")
    static_dir = os.path.join(package_root, "static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Secure random key generation for session management
    app.secret_key = os.urandom(24)

    # --- Authentication Configuration ---
    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        """User loader callback for Flask-Login."""
        return User.get(user_id)

    logger.info(f"Templates initialized at: {os.path.abspath(app.template_folder)}")
    logger.info(f"Static assets initialized at: {os.path.abspath(app.static_folder)}")

    # --- Blueprint Registration ---
    from .routes import main_bp

    app.register_blueprint(main_bp)

    logger.debug("Successfully registered application blueprints and routes.")
    return app


if __name__ == "__main__":
    # Standalone execution for development debugging
    app = create_app()
    logger.warning("Running standalone Flask server (Development Mode).")
    app.run(host="0.0.0.0", port=5000, debug=True)
