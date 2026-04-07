import db
from models.comment import ChildComment, ParentComment


def add_comment(user_id, thread_id, body, parent_comment_id):
    sql = """
        INSERT INTO
            comments (body, user_id, thread_id, parent_comment_id)
        VALUES
            (?, ?, ?, ?)
        """
    db.execute(sql, [body, user_id, thread_id, parent_comment_id])


def collect_comments(thread_id: str | int) -> list[ParentComment]:
    comments = get_comments_on_thread(thread_id)
    if comments == None:
        return []

    parent_comments = {}
    parent_to_child = {}

    for c in comments:
        if c.parent_comment_id:
            if c.parent_comment_id not in parent_to_child:
                parent_to_child[c.parent_comment_id] = {}
            parent_to_child[c.parent_comment_id][c.id] = c
        else:
            parent_comments[c.id] = c

    for p, cs in parent_to_child.items():
        parent_comments[p].children = cs

    return list(parent_comments.values())


def get_comments_on_thread(thread_id):
    rows = db.query(
        """
        SELECT c.id,
               c.body,
               c.user_id,
               c.thread_id,
               c.parent_comment_id,
               c.votes,
               c.created_at,
               u.username
        FROM comments AS c
        JOIN users AS u ON c.user_id = u.id
        WHERE c.thread_id = ?
        ORDER BY c.created_at DESC
        """,
        [thread_id],
    )
    if not rows:
        return None

    return [ParentComment(**c) if "parent_comment_id" not in c else ChildComment(**c) for c in rows]


def get_comment(comment_id):
    comment_rows = db.query(
        """
        SELECT c.id,
               c.body,
               c.user_id,
               c.thread_id,
               c.parent_comment_id
               c.votes,
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

    return {
        "id": comment["id"],
        "body": comment["body"],
        "thread_id": comment["thread_id"],
        "parent_comment_id": comment["parent_comment_id"],
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


def comments_user_has_voted(user_id):
    rows = db.query(
        """
        SELECT comment_id
        FROM votes
        WHERE comment_id IS NOT NULL AND voter_id = ?
    """,
    [user_id],
    )
    return [r[0] for r in rows]
