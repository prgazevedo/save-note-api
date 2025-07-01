# routes/auth.py

import os
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

bp = Blueprint("auth", __name__)

# 🔐 Load admin credentials from environment
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")             # plain (for dev only)
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")   # hashed (recommended for prod)

# 🚨 Validate startup config
if not ADMIN_USERNAME or (not ADMIN_PASSWORD and not ADMIN_PASSWORD_HASH):
    raise RuntimeError("ADMIN_USERNAME and either ADMIN_PASSWORD or ADMIN_PASSWORD_HASH must be set in environment.")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Admin login page (HTML form).
    Accepts POST with username/password and stores session if valid.
    """
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # ✅ Validate user
        if username == ADMIN_USERNAME:
            if ADMIN_PASSWORD_HASH:
                if check_password_hash(ADMIN_PASSWORD_HASH, password):
                    session["authenticated_user"] = username
                    flash("Login successful.", "success")
                    return redirect(url_for("admin.dashboard"))
            elif ADMIN_PASSWORD:
                if password == ADMIN_PASSWORD:
                    session["authenticated_user"] = username
                    flash("Login successful.", "success")
                    return redirect(url_for("admin.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """
    Clears session and logs out user.
    Redirects back to login page.
    """
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
