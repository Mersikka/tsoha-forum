import re
import sqlite3
from datetime import datetime, timezone

from flask import Flask, abort, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db
import threads
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def is_valid_tag_input(tags):
    pattern = re.compile(r'^(?:#\S+(?:\s+#\S+)*)?$')
    if not tags:
        return True
    tags = tags.strip()
    if tags == "":
        return True
    return bool(pattern.fullmatch(tags))


@app.template_filter('tag_text')
def tag_text_filter(t):
    return t[1:]


@app.route("/")
def index():
    all_threads = threads.get_threads()
    return render_template("index.html", threads=all_threads)


@app.route("/find_thread")
def find_thread():
    query = request.args.get("query")
    if query:
        results = threads.find_threads(query)
    else:
        query = ""
        results = []
    return render_template("find_thread.html", query=query, results=results)


@app.route("/threads/<int:thread_id>")
def show_thread(thread_id):
    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)

    # Convert thread["created_at"] to local time
    local_time = datetime.now().astimezone()
    utc_offset = local_time.utcoffset()
    created_time = datetime.strptime(thread["created_at"], r"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    if utc_offset:
        created_time = created_time + utc_offset
    thread["created_at"] = created_time.strftime(r"%Y-%m-%d %H:%M:%S")

    return render_template("show_thread.html", thread=thread)


@app.route("/users/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    threads_by_user = users.get_threads_by_user(user_id)
    if not threads_by_user:
        threads_by_user = []
    return render_template("show_user.html", user=user, threads_by_user=threads_by_user)


@app.route("/threads")
def threads_redirect():
    return redirect("/")


@app.route("/new_thread")
def new_thread():
    require_login()

    return render_template("new_thread.html")


@app.route("/create_thread", methods=["POST"])
def create_thread():
    require_login()

    title = request.form["title"]
    if len(title) > 100 or not title:
        abort(403)
    body = request.form["body"]
    if len(body) > 5000 or not body:
        abort(403)
    tags = request.form["tags"]
    if len(tags) > 100 or not is_valid_tag_input(tags):
        abort(403)

    user_id = session["user_id"]

    threads.add_thread(title, body, tags, user_id)

    return redirect("/")


@app.route("/edit_thread/<int:thread_id>")
def edit_thread(thread_id):
    require_login()

    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    # Convert thread["created_at"] to local time
    local_time = datetime.now().astimezone()
    utc_offset = local_time.utcoffset()
    created_time = datetime.strptime(thread["created_at"], r"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    if utc_offset:
        created_time = created_time + utc_offset
    thread["created_at"] = created_time.strftime(r"%Y-%m-%d %H:%M:%S")

    if thread["tags"]:
        thread["tags"] = " ".join(thread["tags"])
    else:
        del thread["tags"]

    return render_template("edit_thread.html", thread=thread)


@app.route("/update_thread", methods=["POST"])
def update_thread():
    require_login()

    thread_id = request.form["thread_id"]

    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)
    
    title = request.form["title"]
    if len(title) > 100 or not title:
        abort(403)
    body = request.form["body"]
    if len(body) > 5000 or not body:
        abort(403)
    tags = request.form["tags"]
    if len(tags) > 100 or not is_valid_tag_input(tags):
        abort(403)

    threads.update_thread(thread_id, title, body, tags)

    return redirect(f"/threads/{thread_id}")


@app.route("/delete_thread/<int:thread_id>", methods=["GET", "POST"])  # pyright: ignore[reportArgumentType]
def delete_thread(thread_id):
    require_login()

    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("delete_thread.html", thread=thread)

    if request.method == "POST":
        if "remove" in request.form:
            threads.delete_thread(thread_id)
            return redirect("/")
        else:
            return redirect(f"/threads/{thread_id}")


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


@app.route("/login", methods=["GET", "POST"])  # pyright: ignore[reportArgumentType]
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
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
