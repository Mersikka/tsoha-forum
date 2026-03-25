
-- Clear database
DELETE FROM assets;
DELETE FROM users;
DELETE FROM threads;
DELETE FROM comments;
DELETE FROM tags;
DELETE FROM thread_tags;
DELETE FROM votes;

-- Create default account "mio1234"
-- Default password "1234"
INSERT INTO users (id, username, profile_picture, password_hash) VALUES (0, 'mio1234', NULL, 'scrypt:32768:8:1$9YEUjvYO6LxacZfR$43915005f88112dff2ffd39726713e435aedcaa71a8e6e136f40c9edcd69ae16ba0a42691eef880a59c7fb14bac21e184cd9ad7a929e9fb4f445f65fbe6ae19e');

-- Create dummy thread
INSERT INTO threads (id, title, body, user_id) VALUES(0, 'Hello, World!', 'Lorem ipsum dolor sit amet', 0);
