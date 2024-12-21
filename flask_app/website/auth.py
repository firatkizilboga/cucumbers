from flask import Blueprint, render_template, request, redirect, url_for, flash, url_for,abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy import text
from functools import wraps

try:
    db = db
except NameError:
    from .views import db

auth = Blueprint('auth', __name__)

# --------------------------
# 1. FORMS
# --------------------------

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


# --------------------------
# 2. MINIMAL USER CLASS
# --------------------------

class EphemeralUser:
    """
    Minimal user class for Flask-Login, with an interface to
    handle get_id(), is_authenticated, etc. We'll load it from direct queries.
    """
    def __init__(self, user_id, username, password_hash, is_admin):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = bool(is_admin)

    def check_password(self, plain_password):
        """Verify plain text password against stored hash."""
        return hasher.verify(plain_password, self.password_hash)

    # Flask-Login requires these properties/methods:
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


# --------------------------
# 3. HELPER FUNCTIONS
# --------------------------

def get_user_by_username(username):
    """
    Run direct SQL to find user by username.
    Return an EphemeralUser or None.
    """
    query = text("""
        SELECT id, username, password_hash, is_admin
        FROM users
        WHERE username = :uname
        LIMIT 1
    """)
    result = db.session.execute(query, {"uname": username}).fetchone()
    if result:
        return EphemeralUser(*result)
    return None


def get_user_by_id(user_id):
    """
    Run direct SQL to find user by ID.
    Return an EphemeralUser or None.
    """
    query = text("""
        SELECT id, username, password_hash, is_admin
        FROM users
        WHERE id = :uid
        LIMIT 1
    """)
    result = db.session.execute(query, {"uid": user_id}).fetchone()
    if result:
        return EphemeralUser(*result)
    return None


def create_user(username, plain_password, is_admin=False):
    """Insert a new user row with hashed password."""
    password_hash = hasher.hash(plain_password)
    query = text("""
        INSERT INTO users (username, password_hash, is_admin)
        VALUES (:uname, :pwhash, :adminflag)
    """)
    db.session.execute(query, {
        "uname": username,
        "pwhash": password_hash,
        "adminflag": is_admin
    })
    db.session.commit()


# --------------------------
# 4. ROUTES
# --------------------------

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = get_user_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", category="success")
            # If there's a ?next= param, go there; else home
            next_page = request.args.get('next') or url_for('views.homepage')
            return redirect(next_page)
        else:
            flash("Invalid username or password.", category="error")

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for('views.homepage'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        is_admin_flag = form.is_admin.data  # boolean

        # Check if user already exists
        existing = get_user_by_username(username)
        if existing:
            flash("Username already taken.", category="error")
            return redirect(url_for('auth.register'))

        # Otherwise, create user row
        create_user(username, password, is_admin_flag)
        flash("Registration successful. You can now log in.", category="success")
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

def admin_required(route_func):
    """
    A decorator that first requires the user to be logged in,
    then checks if 'is_admin' is True on the current_user.
    If not, abort or redirect.
    """
    @wraps(route_func)
    @login_required  # ensures the user is authenticated
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:

            # Option 2: Flash a message and redirect
            flash("You do not have permission to view this page.", "error")
            return redirect(url_for("views.homepage"))

        # If admin, proceed to the wrapped route
        return route_func(*args, **kwargs)
    return wrapper
