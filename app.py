import math
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from termios import CS5

from flask import Flask, Response, abort, redirect, render_template, request, session

import comments
import config
import threads
import users

app = Flask(__name__, static_folder="static")
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
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
@app.route("/<int:page>")
def index(page=1):
    page_size = 20
    thread_count = threads.count_threads()
    page_count = math.ceil(thread_count / page_size)
    page_count = max(page_count, 1)
    
    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))
    
    all_threads = threads.get_threads(page, page_size)
    return render_template("index.html", threads=all_threads, page=page, page_count=page_count)


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
    if thread:
        if "user_id" in session:
            thread["has_user_voted"] = threads.has_user_voted_thread(
                thread_id, session["user_id"]
            )
            thread["voted_comments"] = comments.comments_user_has_voted(
                session["user_id"]
            )
    
        local_time = datetime.now().astimezone()
        utc_offset = local_time.utcoffset()
        created_time = datetime.strptime(
            thread["created_at"], r"%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)
        if utc_offset:
            created_time = created_time + utc_offset
        thread["created_at"] = created_time.strftime(r"%Y-%m-%d %H:%M:%S")

        thread["comments"] = comments.collect_comments(thread_id)
    else:
        abort(404)

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
    check_csrf()
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


@app.route("/create_comment", methods=["POST"])
def create_comment():
    check_csrf()
    require_login()

    body = request.form["body"]
    thread_id = request.form["thread_id"]
    parent_comment_id = None
    if "parent_comment_id" in request.form:
        parent_comment_id = request.form["parent_comment_id"]
    user_id = session["user_id"]

    if len(body) > 3000 or not body:
        abort(403)

    comments.add_comment(
        user_id=user_id,
        thread_id=thread_id,
        body=body,
        parent_comment_id=parent_comment_id,
    )

    return redirect(f"/threads/{thread_id}")


@app.route("/update_comment", methods=["POST"])
def update_comment():
    check_csrf()
    require_login()

    thread_id = request.form["thread_id"]
    comment_id = request.form["comment_id"]
    body = request.form["body"]

    if len(body) > 3000 or not body:
        abort(403)

    comment = comments.get_comment(comment_id)
    if comment:
        if comment["user_id"] != session["user_id"]:
            abort(403)
    else:
        abort(404)

    comments.update_comment(comment_id, body)

    return redirect(f"/threads/{thread_id}#{comment_id}")


@app.route("/delete_comment", methods=["POST"])
def delete_comment():
    check_csrf()
    require_login()

    thread_id = request.form["thread_id"]
    comment_id = request.form["comment_id"]

    comment = comments.get_comment(comment_id)
    if comment:
        if comment["user_id"] != session["user_id"]:
            abort(403)
    else:
        abort(404)

    comments.delete_comment(comment_id)

    return redirect(f"/threads/{thread_id}")


@app.route("/vote", methods=["POST"])
def vote():
    check_csrf()
    require_login()

    remove_vote = bool(request.form["remove_vote"])
    voter_id = request.form["voter_id"]
    thread_id = request.form["thread_id"]

    if remove_vote:
        threads.unvote_thread(thread_id, voter_id)
    else:
        threads.vote_thread(thread_id, voter_id)

    return redirect(f"/threads/{thread_id}")


@app.route("/vote_comment", methods=["POST"])
def vote_comment():
    check_csrf()
    require_login()

    remove_vote = bool(request.form["remove_vote"])
    voter_id = request.form["voter_id"]
    comment_id = request.form["comment_id"]
    thread_id = request.form["thread_id"]

    if remove_vote:
        comments.unvote_comment(comment_id, voter_id)
    else:
        comments.vote_comment(comment_id, voter_id)

    return redirect(f"/threads/{thread_id}#{comment_id}")


@app.route("/edit_thread/<int:thread_id>")
def edit_thread(thread_id):
    require_login()

    thread = threads.get_thread(thread_id)
    if thread:
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
    else:
        abort(404)

    return render_template("edit_thread.html", thread=thread)


@app.route("/update_thread", methods=["POST"])
def update_thread():
    check_csrf()
    require_login()

    thread_id = request.form["thread_id"]

    thread = threads.get_thread(thread_id)
    if thread:
        if thread["user_id"] != session["user_id"]:
            abort(403)
    else:
        abort(404)
    
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


@app.route("/delete_thread/<int:thread_id>", methods=["POST"])  # pyright: ignore[reportArgumentType]
def delete_thread(thread_id):
    check_csrf()
    require_login()

    thread = threads.get_thread(thread_id)
    if thread:
        if thread["user_id"] != session["user_id"]:
            abort(403)
    else:
        abort(404)

    threads.delete_thread(thread_id)
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
        abort(Response("VIRHE: salasanat eivät täsmää. Sinut uudelleenohjataan 3 sekunnin kuluttua...",
                       headers={"Refresh": "3; url=/register"}))

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        abort(Response("VIRHE: tunnus on jo varattu. Sinut uudelleenohjataan 3 sekunnin kuluttua...",
                       headers={"Refresh": "3; url=/register"}))
    res, user_id = users.check_credentials(username, password1)
    if res:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    abort(500)


@app.route("/login", methods=["GET", "POST"])  # pyright: ignore[reportArgumentType]
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        res, user_id = users.check_credentials(username, password)

        if res:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            abort(Response("VIRHE: väärä tunnus tai salasana. Sinut uudelleenohjataan 3 sekunnin kuluttua...",
                           headers={"Refresh": "3; url=/login"}))


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
        del session["csrf_token"]
    return redirect("/")
