from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from books.models import Book


def index(request):
    return render(request, "library/index.html")

@login_required
def add_book(request):
    """View to add a new book to the library. Only accessible by librarians."""
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to add books.")

    if request.method == "POST":
        isbn = request.POST.get("isbn", "").strip()
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        publisher = request.POST.get("publisher", "").strip()
        subject = request.POST.get("subject", "").strip()

        if not all([isbn, title, author, publisher, subject]):
            return render(request, "library/add_book.html", {"error": "All fields are required."})

        # Create the book instance
        book = Book.objects.create(
            isbn=isbn,
            title=title,
            author=author,
            publisher=publisher,
            subject=subject
        )
        book.save()

        return render(request, "library/add_book.html", {"message": "Book added"})

    # Render the add book form for GET requests
    return render(request, "library/add_book.html")