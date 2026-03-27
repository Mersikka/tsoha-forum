from flask import Response, abort
from werkzeug.security import check_password_hash, generate_password_hash

import db
import threads


def create_user(username, password):
    password_hash = generate_password_hash(password)
    
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])


def check_credentials(username, password):
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])
        if not result:
            abort(Response("VIRHE: väärä tunnus tai salasana. Sinut uudelleenohjataan 3 sekunnin kuluttua...",
                           headers={"Refresh": "3; url=/login"}))
        result = result[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        return (check_password_hash(password_hash, password), user_id)


def get_user(user_id):
    user_rows = db.query(
        """
        SELECT id,
               username,
               votes_received
        FROM users
        WHERE id = ?
        """,
        [user_id],
    )
    if not user_rows:
        return None

    user = user_rows[0]
    return user


def get_thread_ids_by_user(user_id):
    rows = db.query(
        """
        SELECT t.id
        FROM threads AS t
        WHERE t.user_id = ?
        """,
        [user_id],
    )
    if not rows:
        return None
    ids = [row["id"] for row in rows]
    return ids


def get_threads_by_user(user_id):
    thread_ids = get_thread_ids_by_user(user_id)
    if not thread_ids:
        return None
    return [threads.get_thread(id) for id in thread_ids]
