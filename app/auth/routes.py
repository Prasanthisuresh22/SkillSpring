from urllib.parse import urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from extensions import db


def _safe_next_url(target):
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    return target


@auth.route("/login", methods=["GET", "POST"])
@auth.route("/auth/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash("Invalid email or password.", "error")
        else:
            login_user(user, remember=form.remember.data)
            destination = _safe_next_url(request.args.get("next"))
            return redirect(destination or url_for("main.dashboard"))
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
@auth.route("/auth/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        full_name = " ".join(form.full_name.data.strip().split())
        if User.query.filter_by(email=email).first() is not None:
            form.email.errors.append("That email address is already registered.")
        else:
            user = User(full_name=full_name, email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.email.errors.append("That email address is already registered.")
            else:
                flash("Your account is ready. Please log in.", "success")
                return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.post("/logout")
@auth.post("/auth/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))
