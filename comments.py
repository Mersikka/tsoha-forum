import db


def add_comment(user_id, thread_id, body, parent_id, is_child_comment):
    sql = """
        INSERT INTO
            comments (body, user_id, thread_id, parent_thread_id, parent_comment_id)
        VALUES
            (?, ?, ?, ?, ?)
        """
    parent_thread_id, parent_comment_id = None, None
    if is_child_comment:
        parent_comment_id = parent_id
    else:
        parent_thread_id = parent_id
    db.execute(sql, [body, user_id, thread_id, parent_thread_id, parent_comment_id])


def get_comment(comment_id):
    comment_rows = db.query(
        """
        SELECT c.id,
               c.body,
               c.user_id,
               c.thread_id,
               c.parent_thread_id,
               c.parent_comment_id
               c.created_at,
               u.username
        FROM comments AS c
        JOIN users AS u ON c.user_id = u.id
        WHERE c.id = ?
        """,
        [comment_id],
    )
    if not comment_rows:
        return None

    comment = comment_rows[0]

    if "parent_thread_id" in comment:
        parent_id = comment["parent_thread_id"]
        is_child_comment = False
    else:
        parent_id = comment["parent_comment_id"]
        is_child_comment = True

    return {
        "id": comment["id"],
        "body": comment["body"],
        "thread_id": comment["thread_id"],
        "parent_id": parent_id,
        "is_child_comment": is_child_comment,
        "user_id": comment["user_id"],
        "username": comment["username"],
        "created_at": comment["created_at"],
    }


def update_comment(comment_id, body):
    sql = """UPDATE comments
             SET body = ?
             WHERE id = ?"""
    db.execute(sql, [body, comment_id])


def delete_comment(comment_id):
    db.execute("DELETE FROM comments WHERE id = ?", [comment_id])


def get_comment_votes(comment_id):
    rows = db.query(
        """
        SELECT COUNT(id) AS votes,
        FROM votes
        WHERE comment_id = ?
    """,
    [comment_id],
    )

    return rows[0]["votes"]


def vote_comment(comment_id, user_id):
    db.execute(
        """
        INSERT INTO votes (voter_id, comment_id)
        VALUES (?, ?)
    """,
    [user_id, comment_id],
    )


def unvote_comment(comment_id, user_id):
    db.execute(
        """
        DELETE FROM votes
        WHERE voter_id = ? AND comment_id = ?
    """,
    [user_id, comment_id],
    )


def has_user_voted_comment(comment_id, user_id):
    rows = db.query(
        """
        SELECT id
        FROM votes
        WHERE comment_id = ? AND voter_id = ?
    """,
    [comment_id, user_id],
    )
    return bool(rows)
