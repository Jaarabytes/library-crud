#!/bin/bash

# NOTE: The sqlite file already contains seed data.
# There is no need to run the seed script again.
# Enjoy!

DB_PATH="./db.sqlite3"
CURRENT_TIMESTAMP=$(date +%s)
sqlite3 $DB_PATH <<EOF
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 5 CHECK (stock >= 1),
    UNIQUE (title, author)
);

CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    debt REAL NOT NULL DEFAULT 0 CHECK(debt <= 500)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    return_date TEXT,
    rent_fee REAL DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('issued', 'returned')),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
);
EOF
echo "Successfully created books, tables and transactions tables"
echo
echo "Proceeding to seed some data!"

# Initial seed data
# I hope you have read these classics

BOOKS=("The Metamorphosis,Franz Kafka,5" "1984,George Orwell,3", "Crime And Punishment, Fyodor Doestoevsky, 2" "A song of ice and fire,George R R Martin,7")
MEMBERS=("Richard Stallman" "Terry Davis" "Yacine Brahimi")
TRANSACTIONS=("1,1,$CURRENT_TIMESTAMP,'issued'" "2,2,$CURRENT_TIMESTAMP,'issued'" "3,3,$CURRENT_TIMESTAMP,'issued'")
for book in "${BOOKS[@]}"; do
    IFS=',' read -r title author stock <<< "$book"
    sqlite3 $DB_PATH "INSERT INTO books (title, author, stock) VALUES ('$title', '$author', $stock);"
done

for member in "${MEMBERS[@]}"; do
    sqlite3 $DB_PATH "INSERT INTO members (name) VALUES ('$member');"
done

for transaction in "${TRANSACTIONS[@]}"; do
    IFS=',' read -r book_id member_id issue_date status <<< "$transaction"
    sqlite3 $DB_PATH "INSERT INTO transactions (book_id, member_id, issue_date, status) VALUES ($book_id, $member_id, $issue_date, $status);"
    sqlite3 $DB_PATH "UPDATE books SET stock = stock - 1 WHERE book_id = $book_id AND stock > 0;"
done
echo "Database seeded successfully!"
