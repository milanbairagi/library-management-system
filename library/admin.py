from django.contrib import admin
from .models import Library

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'members', 'staff')
    search_fields = ('name', 'address')