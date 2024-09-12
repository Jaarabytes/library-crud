"""
Since the application is used by the librarian only, no need to login
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

"""
Execute a SQL query safely using parameterization.

:param query: SQL query string with placeholders
:param params: Tuple of parameters to be inserted into the query
:return: List of query results

Why not ORMs?

>ORMs can't handle complex SQL queries.
>ORMs are generally bloat
>I can also handle SQL injections by myself (you don't ORMs to do everything for you)
"""

def execute_sql(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def list_books(request):
    query = "SELECT book_id, title, author, stock FROM books;"
    books = execute_sql(query)
    return render(request, 'library/book_list.html', {'books': books})

def add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        stock = request.POST['stock']
        query = "INSERT INTO books (title, author, stock) VALUES (%s, %s, %s)"
        execute_sql(query, [title, author, stock])
        messages.success(request, "Book added successfully.")
        return redirect('list_books')
    return render(request, 'library/add_book.html')

@require_POST
def update_book(request):
    book_id = request.POST.get('id')
    field = request.POST.get('field')
    value = request.POST.get('value')

    allowed_fields = ['title', 'author', 'stock']
    if field not in allowed_fields:
        return JsonResponse({'status': 'error', 'message': 'Invalid field'}, status=400)

    query = f"UPDATE books SET {field} = %s WHERE book_id = %s"
    try:
        rows_affected = execute_sql(query, [value, book_id])
        if rows_affected:
            return JsonResponse({'status': 'success', 'message': 'Book updated successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
def delete_book(request):
    book_id = request.POST.get('id')

    query = "DELETE FROM books WHERE book_id = %s"
    try:
        rows_affected = execute_sql(query, [book_id])
        if rows_affected:
            return JsonResponse({'status': 'success', 'message': 'Book deleted successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def list_members(request):
    query = "SELECT member_id, name, debt FROM members"
    members = execute_sql(query)
    print("Debug - members:", members) 
    return render(request, 'library/member_list.html', {'members': members})

def add_member(request):
    if request.method == 'POST':
        name = request.POST['name']
        outstanding_debt = request.POST['debt']
        query = "INSERT INTO members (name, debt) VALUES (%s, %s)"
        execute_sql(query, [name, outstanding_debt])
        messages.success(request, "Member added successfully.")
        return redirect('list_members')
    return render(request, 'library/add_member.html')

@require_POST
def update_member(request):
    member_id = request.POST.get('id')
    field = request.POST.get('field')
    value = request.POST.get('value')

    allowed_fields = ['name', 'debt']
    if field not in allowed_fields:
        return JsonResponse({'status': 'error', 'message': 'Invalid field'}, status=400)

    if field == 'debt':
        try:
            debt = float(value)
            if debt > 500:
                return JsonResponse({'status': 'error', 'message': 'Debt cannot exceed 500'}, status=400)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid debt value'}, status=400)

    query = f"UPDATE members SET {field} = %s WHERE member_id = %s"
    try:
        rows_affected = execute_sql(query, [value, member_id])
        if rows_affected:
            return JsonResponse({'status': 'success', 'message': 'Member updated successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Member not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
def delete_member(request):
    member_id = request.POST.get('id')

    query = "DELETE FROM members WHERE member_id = %s"
    try:
        rows_affected = execute_sql(query, [member_id])
        if rows_affected:
            return JsonResponse({'status': 'success', 'message': 'Member deleted successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Member not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def issue_book_view(request):
    if request.method == 'POST':
        book_id = request.POST['book_id']
        member_id = request.POST['member_id']
        query = "SELECT stock FROM books WHERE book_id = %s"
        book_stock = execute_sql(query, [book_id])[0][0]
        if book_stock > 0:
            issue_query = """
                INSERT INTO transactions (book_id, member_id, issue_date, status) 
                VALUES (%s, %s, CURRENT_TIMESTAMP, 'issued')
            """
            update_stock_query = "UPDATE books SET stock = stock - 1 WHERE book_id = %s"
            execute_sql(issue_query, [book_id, member_id])
            execute_sql(update_stock_query, [book_id])
            messages.success(request, "Book issued successfully.")
        else:
            messages.error(request, "Book is out of stock.")
        return redirect('list_books')
    members = execute_sql("SELECT member_id, name FROM members")
    books = execute_sql("SELECT book_id, title FROM books")
    return render(request, 'library/issue_book.html', {'members': members, 'books': books})

def return_book_view(request):
    if request.method == 'POST':
        book_id = request.POST['book_id']
        member_id = request.POST['member_id']
        rent_fee = request.POST['rent_fee']

        debt_query = "SELECT debt FROM members WHERE member_id = %s"
        outstanding_debt = execute_sql(debt_query, [member_id])[0][0]
        if outstanding_debt + float(rent_fee) > 500:
            messages.error(request, "Member's outstanding debt exceeds KES 500.")
        else:
            return_query = """
                UPDATE transactions
                SET return_date = CURRENT_TIMESTAMP, rent_fee = %s
                WHERE book_id = %s AND member_id = %s AND return_date IS NULL
            """
            update_stock_query = "UPDATE books SET stock = stock + 1 WHERE book_id = %s"
            update_debt_query = "UPDATE members SET debt = debt + %s WHERE member_id = %s"
            execute_sql(return_query, [rent_fee, book_id, member_id])
            execute_sql(update_stock_query, [book_id])
            execute_sql(update_debt_query, [rent_fee, member_id])
            messages.success(request, "Book returned successfully.")
        return redirect('list_books')
    members = execute_sql("SELECT member_id, name FROM members")
    books = execute_sql("SELECT book_id, title FROM books")
    return render(request, 'library/return_book.html', {'members': members, 'books': books})
