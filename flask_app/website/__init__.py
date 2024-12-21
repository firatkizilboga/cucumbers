from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from .views import views, db

# Assuming app is your Flask instance
app = Flask(__name__)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev secret key'

    MYSQL_USER = "admin"
    MYSQL_PASSWORD = "3Hiyarlar"
    MYSQL_HOST = "134.122.79.205"
    MYSQL_PORT = 3306
    MYSQL_DATABASE = "cucumdb"

    # Set SQLAlchemy configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    app.register_blueprint(views, url_prefix='/')

    return app