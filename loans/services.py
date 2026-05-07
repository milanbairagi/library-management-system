"""Loan service layer: orchestrates book issue, return, and reservation workflows."""

from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from core.constants import LOAN_PERIOD_DAYS, MAX_LOANS_PER_MEMBER
from books.models import BookStatus
from loans.models import Loan, Reservation, ReservationStatus


class LoanService:
    """Encapsulates multi-step book loan workflows with transaction safety."""

    @staticmethod
    @transaction.atomic
    def issue_book(member, book_item, due_date=None):
        """
        Issue a book to a member with validation and state transitions.
        
        Args:
            member: Member instance to issue book to
            book_item: BookItem instance to issue
            due_date: Optional override for due date (defaults to LOAN_PERIOD_DAYS from now)
        
        Returns:
            dict: {
                'success': bool,
                'loan': Loan instance or None,
                'message': str
            }
        
        Raises:
            ValueError: If member or book_item is invalid
        """
        if not member:
            return {'success': False, 'loan': None, 'message': 'Member not found.'}
        if not book_item:
            return {'success': False, 'loan': None, 'message': 'Book item not found.'}

        # Check if book item is available
        if not book_item.check_availability():
            # Try to create a reservation for the member
            existing_reservation = Reservation.objects.filter(
                book=book_item.book,
                member=member,
                status=ReservationStatus.WAITING
            ).first()
            if not existing_reservation:
                Reservation.objects.create(
                    book=book_item.book,
                    member=member,
                    status=ReservationStatus.WAITING
                )
            return {
                'success': False,
                'loan': None,
                'message': 'Book is not available. A reservation has been created for the member.'
            }

        # Check if member has pending fines
        pending_fines = sum(loan.get_pending_fine() for loan in member.loans.all())
        if pending_fines > 0:
            return {
                'success': False,
                'loan': None,
                'message': f'Member has pending fines of ${pending_fines:.2f}. Please resolve fines before issuing new books.'
            }

        # Check if member has reached max active loans
        active_loans_count = member.loans.filter(return_date__isnull=True).count()
        if active_loans_count >= MAX_LOANS_PER_MEMBER:
            return {
                'success': False,
                'loan': None,
                'message': f'Member has reached the maximum number of active loans ({MAX_LOANS_PER_MEMBER}). Cannot issue more books until some are returned.'
            }

        # Calculate due date if not provided
        if due_date is None:
            due_date = timezone.now().date() + timedelta(days=LOAN_PERIOD_DAYS)

        # Create the loan
        loan = Loan.objects.create(
            member=member,
            book_item=book_item,
            issue_date=timezone.now().date(),
            due_date=due_date
        )

        # Mark the book item as issued
        book_item.mark_issued(due_date=due_date)

        # Fulfill any matching reservations for this book by this member
        reservations = Reservation.objects.filter(
            book=book_item.book,
            member=member,
            status=ReservationStatus.WAITING
        )
        for reservation in reservations:
            reservation.fulfill()

        return {
            'success': True,
            'loan': loan,
            'message': 'Book issued successfully.'
        }

    @staticmethod
    @transaction.atomic
    def return_book(book_item, member):
        """
        Return an issued book with fine calculation and state transitions.
        
        Args:
            book_item: BookItem instance being returned
            member: Member instance returning the book
        
        Returns:
            dict: {
                'success': bool,
                'loan': Loan instance or None,
                'fine': Fine instance or None,
                'message': str
            }
        
        Raises:
            ValueError: If book_item or member is invalid
        """
        if not book_item:
            return {
                'success': False,
                'loan': None,
                'fine': None,
                'message': 'Book item not found.'
            }
        if not member:
            return {
                'success': False,
                'loan': None,
                'fine': None,
                'message': 'Member not found.'
            }

        # Validate book item is currently issued
        if book_item.status != BookStatus.ISSUED:
            return {
                'success': False,
                'loan': None,
                'fine': None,
                'message': 'This book item is not currently issued.'
            }

        # Find the active loan for this book and member
        loan = Loan.objects.filter(
            book_item=book_item,
            member=member,
            return_date__isnull=True
        ).first()

        if not loan:
            return {
                'success': False,
                'loan': None,
                'fine': None,
                'message': 'The member did not borrow this book.'
            }

        # Mark book item as returned
        book_item.mark_returned()

        # Close the loan with today's return date
        loan.return_date = timezone.now().date()
        loan.save()

        # Calculate and create fine if late return
        fine = loan.calculate_and_create_fine()

        if fine and not fine.fully_paid:
            return {
                'success': True,
                'loan': loan,
                'fine': fine,
                'message': f'Book returned successfully. A fine of ${fine.amount:.2f} has been incurred for late return.'
            }

        return {
            'success': True,
            'loan': loan,
            'fine': fine,
            'message': 'Book returned successfully. No fines incurred.'
        }

    @staticmethod
    def reserve_book(member, book):
        """
        Reserve a book for a member.
        
        Args:
            member: Member instance making the reservation
            book: Book instance to reserve
        
        Returns:
            dict: {
                'success': bool,
                'reservation': Reservation instance or None,
                'message': str
            }
        """
        if not member:
            return {'success': False, 'reservation': None, 'message': 'Member not found.'}
        if not book:
            return {'success': False, 'reservation': None, 'message': 'Book not found.'}

        # Check if member already has a waiting reservation for this book
        existing_reservation = Reservation.objects.filter(
            book=book,
            member=member,
            status=ReservationStatus.WAITING
        ).first()
        if existing_reservation:
            return {
                'success': False,
                'reservation': existing_reservation,
                'message': 'You already have a reservation for this book.'
            }

        # Create the reservation
        reservation = Reservation.objects.create(
            book=book,
            member=member,
            status=ReservationStatus.WAITING
        )

        return {
            'success': True,
            'reservation': reservation,
            'message': 'Book reserved successfully.'
        }
