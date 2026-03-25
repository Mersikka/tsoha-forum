CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    content BLOB NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    profile_picture INTEGER REFERENCES assets(id),
    password_hash TEXT NOT NULL
);

CREATE TABLE threads (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
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

CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    voter_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    CHECK (
        (thread_id IS NOT NULL AND comment_id IS NULL) OR
        (thread_id IS NULL AND comment_id IS NOT NULL)
    ),
    UNIQUE(voter_id, thread_id),
    UNIQUE(voter_id, comment_id)
);

