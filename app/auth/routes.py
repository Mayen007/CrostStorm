from urllib.parse import urlparse

from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user, login_user, logout_user

from app.auth import new_bp
from app.auth import user_bp
from app.auth.email_user import send_password_reset_email
from app.auth.forms import (
    LoginForm,
    RegistrationForm, ResetPasswordForm,
    ResetPasswordRequestForm
)
from app.models import User

url = "https://example.com/path?query=value"
parsed_url = urlparse(url)
scheme = parsed_url.scheme
netloc = parsed_url.netloc
path = parsed_url.path
query = parsed_url.query


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('user_bp.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('user_bp.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)


@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user_bp.index'))


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app import db
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('user_bp.login'))
    return render_template('auth/register.html', title='Sign up',
                           form=form)


@user_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'primary')
        return redirect(url_for('user_bp.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form, user=current_user)


@new_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from app import db
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('user_bp.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('user_bp.login'))
    return render_template('auth/reset_password.html', form=form, user=current_user)


@new_bp.route('/user')
def user_route():
    return "This is the user route"
