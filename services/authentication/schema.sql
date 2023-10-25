CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
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
