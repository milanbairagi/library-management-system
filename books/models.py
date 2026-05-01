from django.db import models


class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
    def get_details(self):
        return f"ISBN: {self.isbn}, Title: {self.title}, Author: {self.author}, Publisher: {self.publisher}, Subject: {self.subject}"
    

class BookStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    ISSUED = 'issued', 'Issued'
    RESERVED = 'reserved', 'Reserved'


class BookItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=BookStatus.choices, default=BookStatus.AVAILABLE)
    rack_number = models.CharField(max_length=20)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.barcode}"
    
    def check_availability(self):
        return self.status == BookStatus.AVAILABLE
    
    def mark_issued(self, due_date):
        self.status = BookStatus.ISSUED
        self.due_date = due_date
        self.save()

    def mark_returned(self):
        self.status = BookStatus.AVAILABLE
        self.due_date = None
        self.save()