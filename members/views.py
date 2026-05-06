from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .models import Member
from books.models import Book
from members.models import Member
from loans.models import Loan, Reservation, ReservationStatus


def login_for_role(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password.")
            return render(request, "members/login.html")

        login(request, user)
        return redirect("dashboard")

    return render(request, "members/login.html")


def member_register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "members/register.html", {"user_type": "Member"})

        if Member.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return render(request, "members/register.html", {"user_type": "Member"})

        Member.objects.create_member(email=email, name=name, phone=phone, password=password)
        messages.success(request, "Registration successful. You can now log in.")
        return redirect("login")

    return render(request, "members/register.html", {"user_type": "Member"})


def librarian_register(request):
    return HttpResponseForbidden("Librarian accounts are created by staff administrators only.")


@login_required
def dashboard(request):
    if request.user.is_staff:
        total_books = Book.objects.count()
        total_members = Member.objects.filter(is_staff=False).count()
        total_active_loans = Loan.objects.filter(return_date=None).count()
        total_pending_reservations = Reservation.objects.filter(status=ReservationStatus.WAITING).count()
        return render(request, "members/librarian_dashboard.html", {
            "total_books": total_books,
            "total_members": total_members,
            "total_active_loans": total_active_loans,
            "total_pending_reservations": total_pending_reservations
        })

    user_loaned = Loan.objects.filter(member=request.user, return_date=None).all()
    borrowed_books = [loan.book_item for loan in user_loaned]

    return render(request, "members/member_dashboard.html", {"borrowed_books": borrowed_books})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
