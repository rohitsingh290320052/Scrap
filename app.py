# app.py
from flask import Flask, render_template
from config import Config
from extensions import db
from routes.scraper_routes import scraper_bp
from routes.auth_routes import auth_bp
from routes.api_routes import api_bp  # will add below
from flask_login import LoginManager
import json

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)

    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(scraper_bp)  # prefix already '/', inside file we used '/dashboard' etc.
    app.register_blueprint(api_bp, url_prefix='/api')

    # jinja helper to load JSON strings stored in db
    app.jinja_env.filters['loads'] = lambda s: json.loads(s) if s else []

    # simple home route
    @app.route('/')
    def home():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
