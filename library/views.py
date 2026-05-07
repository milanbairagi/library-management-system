from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from books.models import Book, BookItem, BookStatus
from members.models import Member
from loans.services import LoanService


def index(request):
    search_query = request.GET.get("search_query", "").strip()
    if search_query:
        books = Book.objects.filter(title__icontains=search_query) | Book.objects.filter(author__icontains=search_query)
    else:
        books = Book.objects.all()[:10]  # Limit to first 10 books
    return render(request, "library/index.html", {"books": books, "search_query": search_query})

def book_items(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return render(request, "library/book_items.html", {"error": "Book not found."})

    book_items = BookItem.objects.filter(book=book)
    return render(request, "library/book_items.html", {"book": book, "book_items": book_items})
    

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


@login_required
def view_members(request):
    """View to display all members of the library. Only accessible by librarians."""
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view members.")

    members = Member.objects.all()
    return render(request, "library/view_members.html", {"members": members})

@login_required
def issue_book(request):
    """View to issue a book to a member. Only accessible by librarians."""
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to issue books.")

    members = Member.objects.all()
    books = Book.objects.all()

    if request.method == "POST":
        book_id = request.POST.get("book_id")
        member_id = request.POST.get("member_id")

        try:
            book = Book.objects.get(id=book_id)
            member = Member.objects.get(id=member_id)
            book_item = BookItem.objects.filter(book=book, status=BookStatus.AVAILABLE).first()
        except (Book.DoesNotExist, Member.DoesNotExist):
            return render(request, "library/issue_book.html", {"error": "Invalid book or member ID."})

        # Use the service layer to issue the book
        result = LoanService.issue_book(member, book_item)

        if result['success']:
            return render(request, "library/issue_book.html",
                        {
                            "message": result['message'],
                            "members": members,
                            "books": books
                        })
        else:
            return render(request, "library/issue_book.html",
                        {
                            "error": result['message'],
                            "members": members,
                            "books": books
                        })

    return render(request, "library/issue_book.html",
                        {
                            "members": members,
                            "books": books
                        })


@login_required
def return_book(request):
    """View to return a book. Only accessible by librarians."""
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to return books.")
    
    if request.method == "POST":
        book_item_barcode = request.POST.get("book_item_barcode")
        member_id = request.POST.get("member_id")

        try:
            book_item = BookItem.objects.get(barcode=book_item_barcode)
            member = Member.objects.get(id=member_id)
        except (BookItem.DoesNotExist, Member.DoesNotExist):
            return render(request, "library/return_book.html", {
                "error": "Invalid book item or member ID."
            })

        # Use the service layer to return the book
        result = LoanService.return_book(book_item, member)

        if result['success']:
            if result['fine'] and not result['fine'].fully_paid:
                return render(request, "library/return_book.html", {
                    "message": result['message'],
                    "fine": result['fine']
                })
            else:
                return render(request, "library/return_book.html", {
                    "message": result['message']
                })
        else:
            return render(request, "library/return_book.html", {
                "error": result['message']
            })

    return render(request, "library/return_book.html")