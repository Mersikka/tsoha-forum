import db
from re import fullmatch


def add_thread(title, body, tags, user_id):
    sql = """INSERT INTO threads (title, body, user_id)
             VALUES (?, ?, ?)"""
    db.execute(sql, [title, body, user_id])

    # Link tags to thread
    thread_id = db.last_insert_id()
    tags = tags.split(" ")
    re_pattern = r"^#[A-Za-z0-9_\-ÅÄÖåäöÆØæø]+$"
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
               threads.created_at,
               users.id user_id,
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
        "username": thread["username"],
        "created_at": thread["created_at"],
        "user_id": thread["user_id"],
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
    re_pattern = r"^#[A-Za-z0-9_\-ÅÄÖåäöÆØæø]+$"
    if len(tags) > 0:
        for tag in tags:
            if bool(fullmatch(re_pattern, tag)):
                tag_id = db.get_or_create_tag(tag)
                db.link_tag_to_thread(thread_id, tag_id)
