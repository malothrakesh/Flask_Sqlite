from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models.user import User
from flask_login import login_user, logout_user, login_required
from app.models.forms import RegistrationForm
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('book_bp.book_list'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already taken. Please choose a different one.', 'danger')
            return redirect(url_for('auth_bp.register'))

        # Create and save new user using set_password method
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=False
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        # Log the user in
        login_user(new_user)
        flash('🎉 Registration successful! Welcome.', 'success')
        return redirect(url_for('book_bp.book_list'))

    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth_bp.login'))
