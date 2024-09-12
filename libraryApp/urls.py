"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""

from django.urls import path
from library import views
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('books/', permanent=False)),
    path('books/', views.list_books, name='list_books'),
    path('update_book/', views.update_book, name='update_book'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/delete/', views.delete_book, name='delete_book'),
    path('members/', views.list_members, name='list_members'),
    path('members/add/', views.add_member, name='add_member'),
    path('update_member/', views.update_book, name='update_member'),
    path('members/delete/', views.delete_member, name='delete_member'),
    path('transactions/issue/', views.issue_book_view, name='issue_book'),
    path('transactions/return/', views.return_book_view, name='return_book'),
]
