import os


from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS

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
def get_db():
    return SQL("sqlite:///chat.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"])
@login_required
def index():
    db = get_db()
    chat_groups = db.execute("SELECT * FROM chat_group_participants WHERE person_id = ?", session["user_id"])
    if len(chat_groups) == 0:
        return "You have no ongoing chats"
    
    message_dict = {}
    group_names = {}

    for chat_group_row in chat_groups:

        chat_group_id = chat_group_row["chat_group_id"]

        # Get all group names+++++++

        group_name = db.execute("SELECT group_name FROM chat_groups WHERE id = ?", chat_group_id)[0]["group_name"]
        group_names[chat_group_id] = group_name

        # Add all messages to list inside dictionary. group_id: [message]

        message_rows = db.execute("SELECT * FROM messages WHERE chat_group_id = ?", chat_group_id)

        messages = []

        for message_row in message_rows:
            message = message_row["message"]
            messages.append(message)
        
        message_dict[chat_group_id] = messages

    return render_template("index.html", message_dict=message_dict, group_names=group_names)

@app.route("/create_chat_group", methods=["GET", "POST"])
@login_required
def create_chat_group():
    db = get_db()
    if request.method == "GET":
        people = []
        people_rows = db.execute("SELECT * FROM people")
        for row in people_rows:
            people.append((row["id"], row["display_name"]))

        people.sort(key=lambda x: x[1])
        for i in range(len(people)):
            if people[i][0] == session["user_id"]:
                people.pop(i)

        return render_template("create_chat_group.html", people=people)

    elif request.method == "POST":
        accepted_people = request.form.getlist("people")
        if len(accepted_people) == 0:
            return apology("No participants selected")
        if request.form.get("chat_group_name").strip() is None:
            return apology("No chat group name entered")
        print("accepted people", accepted_people)
        chat_group_id = db.execute("INSERT INTO chat_groups (group_name) VALUES (?)", request.form.get("chat_group_name"))
        for person_id in accepted_people:
            db.execute("INSERT INTO chat_group_participants (chat_group_id, person_id, is_owner) VALUES (?, ?, 0)",
            chat_group_id, person_id)
        # Add self.
        db.execute("INSERT INTO chat_group_participants (chat_group_id, person_id, is_owner) VALUES (?, ?, 1)",
            chat_group_id, session["user_id"])
        return redirect("/")

@app.route("")



def user_belongs(user_id, chat_group_id):
    db = get_db()
    group_participants = db.execute("SELECT * FROM chat_group_participants WHERE chat_group_id = ? AND person_id = ?", chat_group_id, user_id)
    if len(group_participants) == 0:
        return False
    else:
        return True

@app.route("/messages/<chat_group_id>", methods=["GET"])
@login_required
def get_messages(chat_group_id=0):
    if chat_group_id == 0:
        return apology("No group id")

    if not user_belongs(session["user_id"], chat_group_id):
        return apology("You are not in this chat group")

    db = get_db()
    message_rows = db.execute("SELECT * FROM messages WHERE chat_group_id = ?", chat_group_id)
    return {"message_rows": message_rows}

@app.route("/new_message/<chat_group_id>", methods=["POST"])
@login_required
def new_message(chat_group_id=0):
    if chat_group_id == 0:
        return apology("No group id")

    if not user_belongs(session["user_id"], chat_group_id):
        return apology("You are not in this chat group")

    message_object = request.json
    print(message_object)
    message = message_object["message"]
    if not message:
        return apology("No message was received")

    db = get_db()
    db.execute("INSERT INTO messages (message, chat_group_id, sender_id) VALUES (?, ?, ?)", message, chat_group_id, session["user_id"])
    return {}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()
    rows = db.execute("SELECT * FROM people WHERE username = ?", username)
    if len(rows) != 1:
        return apology("Username is incorrect or you do not have an account")
    
    if not check_password_hash(rows[0]["password_hash"], password):
        return apology("Username or password is incorrect")
    
    session["user_id"] = rows[0]["id"]

    return redirect("/")

@login_required
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    db = get_db()
    # If the user submitted the form
    if request.method == "POST":
        
        # If the user didn't provide a username
        
        if not request.form.get("username"):
            return apology("MUST PROVIDE USERNAME",403)

        # If the user didn't provide a display name
        if not request.form.get("display_name"):
            return apology("MUST PROVIDE A DISPLAY NAME", 403)
        
        
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
        
        # Check if display name is already in use

        if len(db.execute("SELECT * FROM people WHERE username = :display_name", display_name=request.form.get("display_name"))) != 0:
            return apology("DISPLAY NAME ALREADY IN USE",403)
        



        # Add username, password, and username to the database

        db.execute("INSERT INTO people (display_name, password_hash, username) VALUES (:display_name, :password_hash, :username)", display_name=request.form.get("display_name"), username=request.form.get("username"), password_hash=generate_password_hash(request.form.get("password")))

        # Log user in and make user session

        rows = db.execute("SELECT * FROM people WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        # Redirect user to home page

        return redirect("/")

        
    return render_template("register.html")

