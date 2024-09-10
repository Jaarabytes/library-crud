from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Helper function to execute raw SQL queries
def execute_sql(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

# View to list all books
@login_required
def list_books(request):
    query = "SELECT id, title, author, stock FROM library_book"
    books = execute_sql(query)
    return render(request, 'library/book_list.html', {'books': books})

# View to add a new book
@login_required
def add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        stock = request.POST['stock']
        query = "INSERT INTO library_book (title, author, stock) VALUES (%s, %s, %s)"
        execute_sql(query, [title, author, stock])
        messages.success(request, "Book added successfully.")
        return redirect('list_books')
    return render(request, 'library/add_book.html')

# View to edit a book's details
@login_required
def edit_book(request, book_id):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        stock = request.POST['stock']
        query = "UPDATE library_book SET title = %s, author = %s, stock = %s WHERE id = %s"
        execute_sql(query, [title, author, stock, book_id])
        messages.success(request, "Book updated successfully.")
        return redirect('list_books')
    query = "SELECT id, title, author, stock FROM library_book WHERE id = %s"
    book = execute_sql(query, [book_id])[0]
    return render(request, 'library/edit_book.html', {'book': book})

# View to delete a book
@login_required
def delete_book(request, book_id):
    query = "DELETE FROM library_book WHERE id = %s"
    execute_sql(query, [book_id])
    messages.success(request, "Book deleted successfully.")
    return redirect('list_books')

# View to list all members
@login_required
def list_members(request):
    query = "SELECT id, name, outstanding_debt FROM library_member"
    members = execute_sql(query)
    return render(request, 'library/member_list.html', {'members': members})

# View to add a new member
@login_required
def add_member(request):
    if request.method == 'POST':
        name = request.POST['name']
        outstanding_debt = request.POST['outstanding_debt']
        query = "INSERT INTO library_member (name, outstanding_debt) VALUES (%s, %s)"
        execute_sql(query, [name, outstanding_debt])
        messages.success(request, "Member added successfully.")
        return redirect('list_members')
    return render(request, 'library/add_member.html')

# View to edit a member's details
@login_required
def edit_member(request, member_id):
    if request.method == 'POST':
        name = request.POST['name']
        outstanding_debt = request.POST['outstanding_debt']
        query = "UPDATE library_member SET name = %s, outstanding_debt = %s WHERE id = %s"
        execute_sql(query, [name, outstanding_debt, member_id])
        messages.success(request, "Member updated successfully.")
        return redirect('list_members')
    query = "SELECT id, name, outstanding_debt FROM library_member WHERE id = %s"
    member = execute_sql(query, [member_id])[0]
    return render(request, 'library/edit_member.html', {'member': member})

# View to delete a member
@login_required
def delete_member(request, member_id):
    query = "DELETE FROM library_member WHERE id = %s"
    execute_sql(query, [member_id])
    messages.success(request, "Member deleted successfully.")
    return redirect('list_members')

# View to issue a book to a member
@login_required
def issue_book_view(request):
    if request.method == 'POST':
        book_id = request.POST['book_id']
        member_id = request.POST['member_id']
        query = "SELECT stock FROM library_book WHERE id = %s"
        book_stock = execute_sql(query, [book_id])[0][0]
        if book_stock > 0:
            issue_query = """
                INSERT INTO library_transaction (book_id, member_id, issue_date) 
                VALUES (%s, %s, NOW())
            """
            update_stock_query = "UPDATE library_book SET stock = stock - 1 WHERE id = %s"
            execute_sql(issue_query, [book_id, member_id])
            execute_sql(update_stock_query, [book_id])
            messages.success(request, "Book issued successfully.")
        else:
            messages.error(request, "Book is out of stock.")
        return redirect('list_books')
    members = execute_sql("SELECT id, name FROM library_member")
    books = execute_sql("SELECT id, title FROM library_book")
    return render(request, 'library/issue_book.html', {'members': members, 'books': books})

# View to return a book from a member
@login_required
def return_book_view(request):
    if request.method == 'POST':
        book_id = request.POST['book_id']
        member_id = request.POST['member_id']
        rent_fee = request.POST['rent_fee']

        # Check if the member's outstanding debt is more than KES 500
        debt_query = "SELECT outstanding_debt FROM library_member WHERE id = %s"
        outstanding_debt = execute_sql(debt_query, [member_id])[0][0]
        if outstanding_debt + float(rent_fee) > 500:
            messages.error(request, "Member's outstanding debt exceeds KES 500.")
        else:
            return_query = """
                UPDATE library_transaction
                SET return_date = NOW(), rent_fee = %s
                WHERE book_id = %s AND member_id = %s AND return_date IS NULL
            """
            update_stock_query = "UPDATE library_book SET stock = stock + 1 WHERE id = %s"
            update_debt_query = "UPDATE library_member SET outstanding_debt = outstanding_debt + %s WHERE id = %s"
            execute_sql(return_query, [rent_fee, book_id, member_id])
            execute_sql(update_stock_query, [book_id])
            execute_sql(update_debt_query, [rent_fee, member_id])
            messages.success(request, "Book returned successfully.")
        return redirect('list_books')
    members = execute_sql("SELECT id, name FROM library_member")
    books = execute_sql("SELECT id, title FROM library_book")
    return render(request, 'library/return_book.html', {'members': members, 'books': books})

# Search books by title or author
@login_required
def search_books(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        search_query = "SELECT id, title, author, stock FROM library_book WHERE title LIKE %s OR author LIKE %s"
        books = execute_sql(search_query, ['%' + query + '%', '%' + query + '%'])
        return render(request, 'library/book_list.html', {'books': books, 'search_term': query})

