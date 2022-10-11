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
    if request.method == "GET":

        chat_groups = db.execute("SELECT * FROM chat_group_participants WHERE person_id = ?", session["user_id"])
        if len(chat_groups) == 0:
            return "You have no ongoing chats"
        
        message_dict = {}
        group_names = {}

        for chat_group_row in chat_groups:

            chat_group_id = chat_group_row["chat_group_id"]

            # Get all group names

            group_name = db.execute("SELECT * FROM chat_groups WHERE id = ?", chat_group_id)[0]["group_name"]
            group_names[chat_group_id] = group_name

            # Add all messages to list inside dictionary. group_id: [message]

            message_rows = db.execute("SELECT * FROM messages WHERE chat_group_id = ?", chat_group_id)

            messages = []

            for message_row in message_rows:
                message = message_row["message"]
                messages.append(message)
            
            message_dict[chat_group_id] = messages
    
        return render_template("index.html", message_dict, group_names)




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form.get("username")
    password = request.form.get("password")

    rows = db.execute("SELECT * FROM people WHERE username = ?", username)
    if len(rows) != 1:
        return apology("Username is incorrect or you do not have an account")
    
    if not check_password_hash(rows[0]["password_hash"], password):
        return apology("Username or password is incorrect")
    
    session["user_id"] = rows[0]["id"]

    return redirect("/")



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
        

        # If the user didn't provide a password confirmation

        if not request.form.get("confirmation"):
            return apology("MUST PROVIDE CONFIRMATION",403)

        # If the password and confirmation don't match

        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("PASSWORDS DO NOT MATCH",403)

        # If the username is already in use

        if len(db.execute("SELECT * FROM people WHERE username = :username", username=request.form.get("username"))) != 0:
            return apology("USERNAME ALREADY IN USE",403)
        

        # If the email is already in use

        if len(db.execute("SELECT * FROM people WHERE username = :username", username=request.form.get("username"))) != 0:
            return apology("EMAIL ALREADY IN USE",403)
        
        # Add username, password, and username to the database

        db.execute("INSERT INTO people (display_name, password_hash, username) VALUES (:display_name, :password_hash, :username)", display_name=request.form.get("display_name"), username=request.form.get("username"), password_hash=generate_password_hash(request.form.get("password")))

        # Log user in and make user session

        rows = db.execute("SELECT * FROM people WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        # Redirect user to home page

        return redirect("/")

        
    return render_template("register.html")




    