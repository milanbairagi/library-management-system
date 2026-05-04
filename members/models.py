from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from books.models import BookItem
from .managers import LibrarianManager, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    class Meta:
        abstract = True


class Member(User):
    objects: UserManager = UserManager()

    borrowed_books = models.ManyToManyField("books.BookItem", blank=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="member_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="member_set",
        blank=True,
    )

    def __str__(self):
        return self.name

    def borrow_book(self, book):
        self.borrowed_books.add(book)

    def return_book(self, book):
        self.borrowed_books.remove(book)

    def reserve_book(self, book):
        from loans.models import Reservation

        reservation = Reservation.objects.create(book=book, member=self)
        return reservation


class Librarian(Member):
    objects: LibrarianManager = LibrarianManager()

    class Meta:
        proxy = True
        verbose_name = "Librarian"
        verbose_name_plural = "Librarians"

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
