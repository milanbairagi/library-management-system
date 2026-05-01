from django.contrib import admin
from .models import Book, BookItem


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'author', 'publisher', 'subject')
    search_fields = ('isbn', 'title', 'author', 'publisher', 'subject')

@admin.register(BookItem)
class BookItemAdmin(admin.ModelAdmin):
    list_display = ('book', 'barcode', 'status', 'rack_number', 'due_date')
    search_fields = ('book__title', 'barcode')
    list_filter = ('status',)