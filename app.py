import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import config
import db
import threads

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    all_threads = threads.get_threads()
    return render_template("index.html", threads=all_threads)


@app.route("/threads/<int:thread_id>")
def show_thread(thread_id):
    thread = threads.get_thread(thread_id)

    # Convert thread["created_at"] to local time
    local_time = datetime.now().astimezone()
    utc_offset = local_time.utcoffset()
    thread["created_at"] = datetime.strptime(thread["created_at"], r"%Y-%m-%d %H:%M:%S")
    thread["created_at"] = thread["created_at"] + utc_offset
    thread["created_at"] = thread["created_at"].strftime(r"%Y-%m-%d %H:%M:%S")

    return render_template("show_thread.html", thread=thread)


@app.route("/threads")
def threads_redirect():
    return redirect("/")


@app.route("/new_thread")
def new_thread():
    return render_template("new_thread.html")


@app.route("/create_thread", methods=["POST"])
def create_thread():
    title = request.form["title"]
    body = request.form["body"]
    tags = request.form["tags"]
    user_id = session["user_id"]

    threads.add_thread(title, body, tags, user_id)

    return redirect("/")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
