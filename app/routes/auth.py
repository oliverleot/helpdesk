from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from app.forms import LoginForm, RegisterForm
from app.services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = auth_service.authenticate(form.email.data, form.password.data)
        if user is None:
            flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("auth/login.html", form=form)
        login_user(user)
        return redirect(url_for("tickets.list_tickets"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            auth_service.register_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("auth/register.html", form=form)
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)
