from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from books.models import Book, BookItem, BookStatus
from members.models import Member
from loans.models import Reservation, Loan
from django.utils import timezone


LOAN_PERIOD_DAYS = 14


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
            book_item = BookItem.objects.filter(book=book, status=BookStatus.AVAILABLE).first()
            member = Member.objects.get(id=member_id)
        except (Book.DoesNotExist, Member.DoesNotExist):
            return render(request, "library/issue_book.html", {"error": "Invalid book or member ID."})
        
        # Check if the book item is available for issuing
        if not book_item or not book_item.check_availability():
            # Create a reservation for the member if the book is not available
            Reservation.objects.create(book=book, member=member)
            return render(request, "library/issue_book.html", {"error": "Book is not available for issuing. A reservation has been created for the member."})

        # Check if the member has any pending fines
        pending_fines = sum(loan.get_pending_fine() for loan in member.loans.all())
        if pending_fines > 0:
            return render(request, "library/issue_book.html", {"error": f"Member has pending fines of ${pending_fines:.2f}. Please resolve fines before issuing new books."})

        # Create a new loan for the book and member
        loan = Loan.objects.create(
            member=member,
            book_item=book_item,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=LOAN_PERIOD_DAYS)
        )

        # Mark the book as issued
        book_item.mark_issued(due_date=loan.due_date)

        # Check if the member has any reservations for this book and mark them as fulfilled
        reservations = Reservation.objects.filter(book=book, member=member)
        for reservation in reservations:
            reservation.fulfill()

        return render(request, "library/issue_book.html",
                        {
                          "message": "Book issued successfully.",
                          "members": members,
                            "books": books
                       })
    

    return render(request, "library/issue_book.html", 
                        {
                          "members": members,
                            "books": books
                       })