from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.utils.helpers import render_error_page
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    User login page.
    Handles login form submission and redirects to the homepage on success.
    """
    if request.method == "POST":
        try:
            db = current_app.db
            username = request.form["username"]
            password = request.form["password"]
            user = db.get_user(username, password)
            if user:
                session["user_id"] = user.id
                session["username"] = user.username
                session["total_cart_items"] = db.get_total_cart_items(user.id)
                return redirect(url_for("general.home"))
            else:
                flash("Invalid username or password", "error")
        except Exception as e:
            logging.error(e)
            return render_error_page(e)
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration page.
    Allows new users to register and redirects to login on success.
    """
    if request.method == "POST":
        try:
            db = current_app.db
            username = request.form["username"]
            password = request.form["password"]
            db.create_user(username, password)
            return redirect(url_for("auth.login"))
        except Exception as e:
            return render_error_page(e)
    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    """
    Logs out the user and clears session data.
    """
    session.clear()
    return redirect(url_for("general.home"))
