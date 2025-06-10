from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import click

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev', # Change this in production!
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'app.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import and register blueprints
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.admin import admin_bp # Import admin blueprint
    app.register_blueprint(admin_bp) # Register admin blueprint (default url_prefix='/admin' is in its definition)

    # Import models here to ensure they are registered with SQLAlchemy
    from . import models

    # CLI command to make a user admin
    @app.cli.command('make-admin')
    @click.argument('username')
    def make_admin_command(username):
        from app.models import User # Import here to avoid circular dependency at module level
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_admin = True
            db.session.commit()
            click.echo(f'User {username} is now an admin.')
        else:
            click.echo(f'User {username} not found.')

    with app.app_context():
        db.create_all() # Create database tables for our data models

    return app
