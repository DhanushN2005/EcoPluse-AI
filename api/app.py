from flask import Flask
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_login import LoginManager, UserMixin

from .models import User

def create_app():
    # Use absolute paths based on the package root
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(package_root, 'templates')
    static_dir = os.path.join(package_root, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir, 
                static_folder=static_dir)
    
    app.secret_key = os.urandom(24)
    
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    print(f"[DEBUG] Template folder: {os.path.abspath(app.template_folder)}")
    print(f"[DEBUG] Static folder: {os.path.abspath(app.static_folder)}")

    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Print registered routes for debugging
    print("[DEBUG] Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
