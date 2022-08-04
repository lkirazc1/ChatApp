import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/register", methods=["GET","POST"])
def register():
    # If the user sumbited the form
    if request.method == "POST":
        # If the user didn't provide a username
        if not request.form.get("username"):
            return apology("MUST PROVIDE USERNAME",403)
        # If the user didn't provide a password
        if not request.form.get("password"):
            return apology("MUST PROVIDE PASSWORD",403)
        # If the user didn't provide a email
        if not request.form.get("email"):
            return apology("MUST PROVIDE EMAIL",403)    
        # If the email is invalid
        email = request.form.get()
        if "." not in email or indices[i] <  or "@" not in email:
                return apology("INVALID EMAIL",403)
            
    