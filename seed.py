import random
import sqlite3

from werkzeug.security import generate_password_hash

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM threads")
db.execute("DELETE FROM comments")
db.execute("DELETE FROM tags")
db.execute("DELETE FROM thread_tags")
db.execute("DELETE FROM votes")

user_count = 1000
thread_count = 10**5
parent_comment_count = 10**6
children_per_parent = 2

default_hash = generate_password_hash("123")

print(f"Seeding {user_count} users...")
for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               ["user" + str(i), default_hash])
print("Done!")

print(f"Seeding {thread_count} threads...")
for i in range(1, thread_count + 1):
    user_id = random.randint(1, user_count)
    db.execute("INSERT INTO threads (title, body, user_id) VALUES (?, ?, ?)",
               ["thread title" + str(i), "thread body" + str(i), user_id])
print("Done!")

print(f"Seeding {parent_comment_count} parent comments with {children_per_parent} child comments each...")
for i in range(1, parent_comment_count + 1):
    user_id = random.randint(1, user_count)
    thread_id = random.randint(1, thread_count)
    db.execute("INSERT INTO comments (id, body, user_id, thread_id) VALUES (?, ?, ?, ?)",
               [i, "parent comment body" + str(i), user_id, thread_id])
    for j in range(1, children_per_parent + 1):
        user_id = random.randint(1, user_count)
        db.execute("INSERT INTO comments (id, body, user_id, thread_id, parent_comment_id) VALUES (?, ?, ?, ?, ?)",
                   [parent_comment_count + (i-1) * children_per_parent + j, "child comment body" + str(i), user_id, thread_id, i])
print("Done!")

db.commit()
db.close()
