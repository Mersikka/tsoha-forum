import db
import threads


def get_user(user_id):
    user_rows = db.query(
        """
        SELECT id,
               username
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
