CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE threads (
    id INTEGER PRIMARY KEY,
    title TEXT,
    body TEXT,
    user_id INTEGER REFERENCES users,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    tag_name TEXT UNIQUE
);

CREATE TABLE thread_tags (
    thread_id INTEGER REFERENCES threads(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (thread_id, tag_id)
);
