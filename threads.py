from re import fullmatch

import db


def add_thread(title, body, tags, user_id, asset_id=None):
    sql = """INSERT INTO threads (title, body, asset_id, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, body, asset_id, user_id])

    # Link tags to thread
    thread_id = db.last_insert_id()
    tags = tags.split()
    re_pattern = r"^#[A-Za-z0-9_\-ÅÄÖåäöÆØæø]+"
    if len(tags) > 0:
        for tag in tags:
            if bool(fullmatch(re_pattern, tag)):
                tag_id = db.get_or_create_tag(tag)
                db.link_tag_to_thread(thread_id, tag_id)


def get_threads():
    sql = "SELECT id, title, created_at FROM threads ORDER BY id DESC"

    return db.query(sql)


def get_thread(thread_id):
    thread_rows = db.query(
        """
        SELECT threads.id,
               threads.title,
               threads.body,
               threads.asset_id,
               threads.created_at,
               users.id user_id,
               threads.votes,
               threads.number_of_comments,
               users.username
        FROM threads
        JOIN users ON threads.user_id = users.id
        WHERE threads.id = ?
        """,
        [thread_id],
    )
    if not thread_rows:
        return None

    thread = thread_rows[0]

    tag_rows = db.query(
        """
        SELECT tags.tag_name
        FROM tags
        JOIN thread_tags ON tags.id = thread_tags.tag_id
        WHERE thread_tags.thread_id = ?
        """,
        [thread_id],
    )
    tags = [row["tag_name"] for row in tag_rows]

    return {
        "title": thread["title"],
        "body": thread["body"],
        "asset_id": thread["asset_id"],
        "username": thread["username"],
        "created_at": thread["created_at"],
        "user_id": thread["user_id"],
        "votes": thread["votes"],
        "number_of_comments": thread["number_of_comments"],
        "id": thread["id"],
        "tags": tags,
    }


def update_thread(thread_id, title, body, tags):
    sql = """UPDATE threads
             SET title = ?, body = ?
             WHERE id = ?"""
    db.execute(sql, [title, body, thread_id])

    db.execute("DELETE FROM thread_tags WHERE thread_id = ?", [thread_id])
    tags = tags.split(" ")
    re_pattern = r"^#[A-Za-z0-9_\-ÅÄÖåäöÆØæø]+"
    for tag in tags:
        if bool(fullmatch(re_pattern, tag)):
            tag_id = db.get_or_create_tag(tag)
            db.link_tag_to_thread(thread_id, tag_id)


def delete_thread(thread_id):
    db.execute("DELETE FROM thread_tags WHERE thread_id = ?", [thread_id])
    db.execute("DELETE FROM threads WHERE id = ?", [thread_id])
    db.execute(
        """
        DELETE FROM tags
        WHERE id NOT IN (SELECT tag_id FROM thread_tags)
    """
    )


def find_threads(search):
    sql = """
        SELECT
            t.id,
            t.title,
            t.body,
            t.user_id,
            t.created_at,
            GROUP_CONCAT(DISTINCT ts.tag_name), "," AS tags
        FROM threads AS t
        LEFT JOIN thread_tags AS tt ON tt.thread_id = t.id
        LEFT JOIN tags AS ts ON ts.id = tt.tag_id
        WHERE
            LOWER(t.title) LIKE LOWER(:query)
            OR LOWER(t.body) LIKE LOWER(:query)
            OR LOWER(ts.tag_name) LIKE LOWER(:query)
        GROUP BY t.id, t.title, t.body, t.user_id, t.created_at
        ORDER BY t.created_at DESC
    """
    return db.query(sql, {"query": f"%{search}%"})


def vote_thread(thread_id, user_id):
    db.execute(
        """
        INSERT INTO votes (voter_id, thread_id)
        VALUES (?, ?)
    """,
    [user_id, thread_id],
    )


def unvote_thread(thread_id, user_id):
    db.execute(
        """
        DELETE FROM votes
        WHERE voter_id = ? AND thread_id = ?
    """,
    [user_id, thread_id],
    )


def has_user_voted_thread(thread_id, user_id):
    rows = db.query(
        """
        SELECT id
        FROM votes
        WHERE 1 = 1 AND thread_id = ? AND voter_id = ?
    """,
    [thread_id, user_id],
    )
    return bool(rows)
