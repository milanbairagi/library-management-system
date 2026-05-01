from django.db import models
from books.models import BookItem


class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    borrowed_books = models.ManyToManyField('books.BookItem', blank=True)

    def __str__(self):
        return self.name
    
    def borrow_book(self, book):
        self.borrowed_books.add(book)

    def return_book(self, book):
        self.borrowed_books.remove(book)

    def reserve_book(self, book):
        # TODO: Implement reservation logic
        pass


class Libarian(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
    
    def add_book(self, book: BookItem):
        book.save()

    def remove_book(self, book: BookItem):
        book.delete()

    def issue_book(self, book: BookItem, member: Member):
        if book.check_availability():
            book.mark_issued(due_date=None)  # TODO: Set due date
            member.borrow_book(book)

    