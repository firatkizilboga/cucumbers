from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .views import db, views
from .auth import auth

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev secret key'

    # Example MySQL config
    MYSQL_USER = "admin"
    MYSQL_PASSWORD = "31cuCUMbers"
    MYSQL_HOST = "134.122.79.205"
    MYSQL_PORT = 3306
    MYSQL_DATABASE = "cucumdb"

    # Configure SQLAlchemy with MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Name of our login route
    login_manager.init_app(app)

    from .auth import get_user_by_id
    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
