import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
#app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///chat.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    pass

@app.route("/register", methods=["GET","POST"])
def register():
    # If the user submitted the form
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
        
        email = request.form.get("email")
        
        if not email.count("@") == 1 or not email.count(".") == 1 or email.index("@") < email.index("."):
            return apology("INVALID EMAIL",403)

        # If the user didn't provide a password confirmation

        if not request.form.get("confirmation"):
            return apology("MUST PROVIDE CONFIRMATION",403)

        # If the password and confirmation don't match

        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("PASSWORDS DO NOT MATCH",403)

        # If the username is already in use

        if len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) != 0:
            return apology("USERNAME ALREADY IN USE",403)
        

        # If the email is already in use

        if len(db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))) != 0:
            return apology("EMAIL ALREADY IN USE",403)
        
        # Add username, password, and email to the database

        rows = db.execute("INSERT INTO users (username, hash, email) VALUES (:username, :hash, :email)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")), email=request.form.get("email"))

        # Log user in and make user session

        session["user_id"] = rows[0]["id"]

        # Redirect user to home page

        return redirect("/")

        
    return render_template("register.html")




    