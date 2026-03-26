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
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    CHECK (
        (thread_id IS NOT NULL AND parent_id IS NULL) OR
        (thread_id IS NULL AND parent_id IS NOT NULL)
    )
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


-- Count votes per thread
CREATE INDEX votes_thread_id ON votes(thread_id)
WHERE thread_id IS NOT NULL;

-- Count votes per comment
CREATE INDEX votes_comment_id ON votes(comment_id)
WHERE comment_id IS NOT NULL;

-- Count total votes a user has received
CREATE INDEX thread_id_to_user_id ON threads(user_id);
CREATE INDEX comment_id_to_user_id ON comments(user_id);
CREATE INDEX vote_id_to_thread_id ON votes(thread_id);
CREATE INDEX vote_id_to_comment_id ON votes(comment_id);
