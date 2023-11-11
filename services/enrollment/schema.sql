CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments (id)
);

CREATE TABLE sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL REFERENCES courses (id),
    classroom TEXT, -- NULL if online
    capacity INTEGER NOT NULL,
    waitlist_capacity INTEGER NOT NULL,
    day TEXT NOT NULL,
    begin_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    instructor_id INTEGER NOT NULL,
    freeze BOOLEAN NOT NULL DEFAULT FALSE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE enrollments (
    user_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL REFERENCES sections (id),
    status TEXT NOT NULL,
    grade TEXT,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, section_id)
);

CREATE TABLE waitlist (
    user_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL REFERENCES sections (id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    position INTEGER NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, section_id)
);
