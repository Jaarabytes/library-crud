"""
Author: Jaarabytes

Why not use Django ORMs? 
ORMs can't handle complex SQL queries, which will be necessary since my app, no matter how small, will scale.

Schema:

-- Books table: stores details about each book
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);

-- Members table: stores details about library members
CREATE TABLE members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    debt REAL NOT NULL DEFAULT 0 CHECK(debt <= 500) -- Max outstanding debt is 500
);

-- Transactions table: stores issue and return details for books
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL, -- Store date as TEXT for SQLite
    return_date TEXT, -- Nullable until returned
    rent_fee REAL DEFAULT 0, -- Rent fee applied when returned
    status TEXT NOT NULL CHECK(status IN ('issued', 'returned')), -- Status of the transaction
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);
"""


from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    stock = models.PositiveIntegerField(default=0)

class Member(models.Model):
    name = models.CharField(max_length=255)
    debt = models.DecimalField(max_digits=6, decimal_places=2, default=0)

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    rent_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length=8)

