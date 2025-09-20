import sqlite3
from flask import g


def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()


def last_insert_id():
    return g.last_insert_id


def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result


def get_or_create_tag(tag_name):
    existing = query("SELECT id FROM tags WHERE tag_name = ?", [tag_name])

    if existing:
        return existing[0]["id"]
    else:
        execute("INSERT INTO tags (tag_name) VALUES (?)", [tag_name])
        return last_insert_id()


def link_tag_to_thread(thread_id, tag_id):
    existing = query(
        "SELECT 1 FROM thread_tags WHERE thread_id = ? AND tag_id = ?",
        [thread_id, tag_id],
    )

    if not existing:
        execute(
            "INSERT INTO thread_tags (thread_id, tag_id) VALUES (?, ?)",
            [thread_id, tag_id],
        )
