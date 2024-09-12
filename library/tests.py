from django.test import TestCase
from django.db import connection

class LibraryTestCase(TestCase):
# ========================================
# SET UP THE DATABASE
# ========================================    
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    debt REAL NOT NULL DEFAULT 0 CHECK(debt <= 500)
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    stock INTEGER NOT NULL DEFAULT 5 CHECK (stock >= 1),
                    UNIQUE (title, author)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    member_id INTEGER NOT NULL,
                    issue_date TEXT NOT NULL,
                    return_date TEXT,
                    rent_fee REAL DEFAULT 0,
                    status TEXT NOT NULL CHECK(status IN ('issued', 'returned')),
                    FOREIGN KEY (book_id) REFERENCES books(book_id),
                    FOREIGN KEY (member_id) REFERENCES members(member_id)
                );
            """)

            cursor.execute("INSERT INTO members (name, debt) VALUES ('John Doe', 50.00)")
            cursor.execute("INSERT INTO books (title, author, stock) VALUES ('1984', 'George Orwell', 3)")

# ========================================
# TESTS START HERE
# ========================================    

    def test_insert_new_member(self):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO members (name, debt) VALUES ('Jane Smith', 100.00)")
            cursor.execute("SELECT * FROM members WHERE name = 'Jane Smith'")
            result = cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'Jane Smith')
        self.assertEqual(result[2], 100.00)

    def test_insert_transaction(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT member_id FROM members WHERE name = 'John Doe'")
            member_id = cursor.fetchone()[0]

            cursor.execute("SELECT book_id FROM books WHERE title = '1984' AND author = 'George Orwell'")
            book_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO transactions (book_id, member_id, issue_date, status) 
                VALUES (%s, %s, '2024-09-01', 'issued')
            """, [book_id, member_id])

            # Verify the transaction was inserted
            cursor.execute("""
                SELECT * FROM transactions WHERE member_id = %s AND book_id = %s
            """, [member_id, book_id])
            result = cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[1], book_id)
        self.assertEqual(result[2], member_id)
        self.assertEqual(result[3], '2024-09-01')
        self.assertEqual(result[6], 'issued')

    def test_debt_constraint(self):
        with connection.cursor() as cursor:
            with self.assertRaises(Exception):
                cursor.execute("INSERT INTO members (name, debt) VALUES ('Mark Jones', 600.00)")

    def test_status_constraint(self):
        with connection.cursor() as cursor:
            # Invalid status _> Exception should be raised
            with self.assertRaises(Exception):
                cursor.execute("""
                    INSERT INTO transactions (book_id, member_id, issue_date, status) 
                    VALUES (1, 1, '2024-09-01', 'pending')
                """)
    def test_add_book_with_zero_stock(self):
        # Test adding a book with zero stock (should fail)
        with connection.cursor() as cursor:
            with self.assertRaises(Exception):
                cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Brave New World', 'Aldous Huxley', 0)")

    def test_add_book_with_negative_stock(self):
        # Test adding a book with negative stock (should fail)
        with connection.cursor() as cursor:
            with self.assertRaises(Exception):
                cursor.execute("INSERT INTO books (title, author, stock) VALUES ('Fahrenheit 451', 'Ray Bradbury', -1)")

    def test_insert_duplicate_title_and_author(self):
        # Test inserting a duplicate title and author (should fail)
        with connection.cursor() as cursor:
            with self.assertRaises(Exception):
                cursor.execute("INSERT INTO books (title, author, stock) VALUES ('1984', 'George Orwell', 5)")


# ========================================
# TESTS END HERE
# ========================================
    def tearDown(self):
        # Drop the tables after each test
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS transactions")
            cursor.execute("DROP TABLE IF EXISTS books")
            cursor.execute("DROP TABLE IF EXISTS members")

