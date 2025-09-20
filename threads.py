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
