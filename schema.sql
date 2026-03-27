CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    content BLOB NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    profile_picture INTEGER REFERENCES assets(id),
    password_hash TEXT NOT NULL,
    votes_received INTEGER DEFAULT 0
);

CREATE TABLE threads (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    votes INTEGER DEFAULT 0,
    number_of_comments INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    body TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id),
    thread_id INTEGER REFERENCES threads(id) ON DELETE CASCADE,
    parent_comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    votes INTEGER DEFAULT 0,
    number_of_children INTEGER DEFAULT 0,
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

-- Triggers for counting comment votes
CREATE TRIGGER
    increment_comment_votes
AFTER INSERT ON
    votes
WHEN
    NEW.thread_id IS NULL
BEGIN
    UPDATE
        comments
    SET
        votes = votes + 1
    WHERE
        id = NEW.comment_id;
    UPDATE
        users
    SET
        votes_received = votes_received + 1
    FROM
        (
            SELECT
                c.user_id
            FROM
                comments AS c
            WHERE
                NEW.comment_id = c.id
        ) AS user_id
    WHERE
        id = user_id;
END;

CREATE TRIGGER
    decrement_comment_votes
AFTER DELETE ON
    votes
WHEN
    OLD.thread_id IS NULL
BEGIN
    UPDATE
        comments
    SET
        votes = votes - 1
    WHERE
        id = OLD.comment_id;
    UPDATE
        users
    SET
        votes_received = votes_received - 1
    FROM
        (
            SELECT
                c.user_id
            FROM
                comments AS c
            WHERE
                OLD.comment_id = c.id
        ) AS user_id
    WHERE
        id = user_id;
END;

-- Triggers for counting thread votes
CREATE TRIGGER
    increment_thread_votes
AFTER INSERT ON
    votes
WHEN
    NEW.comment_id IS NULL
BEGIN
    UPDATE
        threadsSovellusta testattu suurella tietomäärällä ja raportoitu tulokset
    SET
        votes = votes + 1
    WHERE
        id = NEW.thread_id;
    UPDATE
        users
    SET
        votes_received = votes_received + 1
    FROM
        (
            SELECT
                t.user_id
            FROM
                threads AS t
            WHERE
                NEW.thread_id = t.id
        ) AS user_id
    WHERE
        id = user_id;
END;

CREATE TRIGGER
    decrement_thread_votes
AFTER DELETE ON
    votes
WHEN
    OLD.comment_id IS NULL
BEGIN
    UPDATE
        threads
    SET
        votes = votes - 1
    WHERE
        id = OLD.thread_id;
    UPDATE
        users
    SET
        votes_received = votes_received - 1
    FROM
        (
            SELECT
                t.user_id
            FROM
                threads AS t
            WHERE
                OLD.thread_id = t.id
        ) AS user_id
    WHERE
        id = user_id;
END;

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
