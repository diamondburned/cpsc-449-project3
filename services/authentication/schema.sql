CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
    -- PBKDF2 hash, $ format
    -- See https://til.simonwillison.net/python/password-hashing-with-pbkdf2
    passhash TEXT NOT NULL
);

CREATE TABLE user_roles (
    user_id INTEGER NOT NULL REFERENCES users (id),
    role TEXT NOT NULL
        CHECK (role IN ('Student', 'Instructor', 'Registrar')),
    PRIMARY KEY (user_id, role)
);

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users (id),
    token TEXT NOT NULL UNIQUE,
    expiry INTEGER NOT NULL -- UNIX timestamp
);
