from django.db import models
from members.models import Member, Libarian
from books.models import Book

class Library(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    @property
    def members(self):
        return Member.objects.all()

    @property
    def staff(self):
        return Libarian.objects.all()

    def add_book(self, book):
        book.save()

    def remove_book(self, book):
        book.delete()

    def register_member(self, member):
        #TODO: Implement member registration logic
        pass

    def find_book(self, title):
        #TODO: Implement book search logic
        pass