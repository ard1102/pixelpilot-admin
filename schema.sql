-- schema.sql
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    price REAL,
    date_uploaded TIMESTAMP,
    trash_date TIMESTAMP
);