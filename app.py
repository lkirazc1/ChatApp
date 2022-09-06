import os
import re
import sqlite3

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

# Configure SQLite database
connection = sqlite3.connect("chat.db")
db = connection.cursor()

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
    return render_template("index.html")

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
        
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not (re.fullmatch(regex, email)):
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

@app.route("/login", methods=["GET","POST"])
def login():
    # If the user submitted the form
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # If the user hasn't provided a username
        if not username:
            return apology("MUST PROVIDE USERNAME",403)
        # If the password isn't provided
        if not password:
            return apology("MUST PROVIDE PASSWORD",403)
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", username) 
        
        # If username doesn't exist
        if rows == []:
            return apology("INVALID USERNAME",403)
        
        # If password is incorrect
        if check_password_hash(rows[0]["hash"]) != password:
            return apology("INVALID PASSWORD",403)
        
        # Redirects the user to home page
        return render_template("index.html")
    
    return render_template("login.html")


@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    pass

