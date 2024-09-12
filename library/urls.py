from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_books, name='book_list'),
    path('create/', views.add_book, name='book_create'),
    path('update/<int:pk>/', views.edit_book, name='book_update'),
    path('delete/<int:pk>/', views.delete_book, name='book_delete'),
]
