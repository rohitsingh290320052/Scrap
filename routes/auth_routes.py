from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db, login_manager
from models import User

auth_bp = Blueprint('auth', __name__)


# Flask-Login loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- LOGIN PAGE ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('scraper.dashboard'))

        flash("Invalid username or password", "danger")

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('auth.register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# --- LOGOUT ---
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
