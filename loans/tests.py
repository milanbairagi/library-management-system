from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from members.models import Member
from books.models import Book, BookItem, BookStatus
from loans.models import Loan, Fine, Reservation, ReservationStatus
from loans.services import LoanService
from core.constants import LOAN_PERIOD_DAYS, MAX_LOANS_PER_MEMBER, FINE_PER_DAY


class LoanServiceTestCase(TestCase):
    """Test suite for LoanService business logic."""

    def setUp(self):
        """Create test fixtures: member, books, and book items."""
        self.member = Member.objects.create_member(
            email='member@test.com',
            name='Test Member',
            phone='1234567890',
            password='password123'
        )

        self.book1 = Book.objects.create(
            isbn='978-0-13-110362-7',
            title='The C Programming Language',
            author='Brian W. Kernighan',
            publisher='Prentice Hall',
            subject='Programming'
        )

        self.book2 = Book.objects.create(
            isbn='978-0-201-63361-0',
            title='Design Patterns',
            author='Gang of Four',
            publisher='Addison-Wesley',
            subject='Software Design'
        )

        self.book_item1 = BookItem.objects.create(
            book=self.book1,
            barcode='BARCODE001',
            status=BookStatus.AVAILABLE,
            rack_number='A1'
        )

        self.book_item2 = BookItem.objects.create(
            book=self.book2,
            barcode='BARCODE002',
            status=BookStatus.AVAILABLE,
            rack_number='A2'
        )

    def test_issue_book_success(self):
        """Test successful book issue: creates loan, marks book issued, fulfills reservation."""
        result = LoanService.issue_book(self.member, self.book_item1)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['loan'])
        self.assertEqual(result['message'], 'Book issued successfully.')

        # Verify loan was created
        loan = result['loan']
        self.assertEqual(loan.member, self.member)
        self.assertEqual(loan.book_item, self.book_item1)
        self.assertIsNone(loan.return_date)

        # Verify book item is now issued
        self.book_item1.refresh_from_db()
        self.assertEqual(self.book_item1.status, BookStatus.ISSUED)
        self.assertIsNotNone(self.book_item1.due_date)

        # Verify due date is set correctly
        expected_due_date = timezone.now().date() + timedelta(days=LOAN_PERIOD_DAYS)
        self.assertEqual(loan.due_date, expected_due_date)

    def test_issue_book_unavailable(self):
        """Test book issue when book item is unavailable: creates reservation."""
        self.book_item1.status = BookStatus.ISSUED
        self.book_item1.save()

        result = LoanService.issue_book(self.member, self.book_item1)

        self.assertFalse(result['success'])
        self.assertIsNone(result['loan'])
        self.assertIn('not available', result['message'])

        # Verify reservation was created
        reservation = Reservation.objects.filter(book=self.book1, member=self.member).first()
        if not reservation:
            self.fail("Expected a reservation to be created when book is unavailable.")
        self.assertEqual(reservation.status, ReservationStatus.WAITING)

    def test_issue_book_member_has_pending_fines(self):
        """Test book issue rejected when member has pending fines."""
        # Create a loan and fine for the member
        loan = Loan.objects.create(
            member=self.member,
            book_item=self.book_item1,
            issue_date=timezone.now().date() - timedelta(days=10),
            due_date=timezone.now().date() - timedelta(days=5),
            return_date=timezone.now().date() - timedelta(days=2)
        )
        fine = Fine.objects.create(loan=loan, amount=10.00, paid=False)

        result = LoanService.issue_book(self.member, self.book_item2)

        self.assertFalse(result['success'])
        self.assertIn('pending fines', result['message'])

    def test_issue_book_max_loans_reached(self):
        """Test book issue rejected when member reaches max active loans."""
        # Create max loans for the member
        for i in range(MAX_LOANS_PER_MEMBER):
            book = Book.objects.create(
                isbn=f'978-0-13-110362-{i}',
                title=f'Book {i}',
                author='Test Author',
                publisher='Test Publisher',
                subject='Test'
            )
            book_item = BookItem.objects.create(
                book=book,
                barcode=f'BARCODE{100+i}',
                status=BookStatus.AVAILABLE,
                rack_number=f'A{i}'
            )
            Loan.objects.create(
                member=self.member,
                book_item=book_item,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=LOAN_PERIOD_DAYS),
                return_date=None
            )
            book_item.mark_issued(due_date=timezone.now().date() + timedelta(days=LOAN_PERIOD_DAYS))

        # Try to issue another book
        new_book = Book.objects.create(
            isbn='978-0-13-999999-9',
            title='Extra Book',
            author='Test Author',
            publisher='Test Publisher',
            subject='Test'
        )
        new_book_item = BookItem.objects.create(
            book=new_book,
            barcode='BARCODE999',
            status=BookStatus.AVAILABLE,
            rack_number='A99'
        )

        result = LoanService.issue_book(self.member, new_book_item)

        self.assertFalse(result['success'])
        self.assertIn('maximum number of active loans', result['message'])

    def test_return_book_on_time(self):
        """Test book return on time: no fine created."""
        # Create and issue a loan
        loan = Loan.objects.create(
            member=self.member,
            book_item=self.book_item1,
            issue_date=timezone.now().date() - timedelta(days=5),
            due_date=timezone.now().date() + timedelta(days=5)
        )
        self.book_item1.mark_issued(due_date=loan.due_date)

        result = LoanService.return_book(self.book_item1, self.member)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['loan'])
        self.assertIsNone(result['fine'])
        self.assertIn('No fines incurred', result['message'])

        # Verify loan is closed
        loan.refresh_from_db()
        self.assertIsNotNone(loan.return_date)

        # Verify book item is available again
        self.book_item1.refresh_from_db()
        self.assertEqual(self.book_item1.status, BookStatus.AVAILABLE)

    def test_return_book_late(self):
        """Test book return late: fine is created."""
        # Create a loan due yesterday
        loan = Loan.objects.create(
            member=self.member,
            book_item=self.book_item1,
            issue_date=timezone.now().date() - timedelta(days=10),
            due_date=timezone.now().date() - timedelta(days=1)
        )
        self.book_item1.mark_issued(due_date=loan.due_date)

        result = LoanService.return_book(self.book_item1, self.member)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['fine'])
        self.assertFalse(result['fine'].fully_paid)
        self.assertIn('fine of', result['message'])

        # Verify fine amount is correct (1 day late * FINE_PER_DAY)
        expected_fine = 1 * FINE_PER_DAY
        self.assertEqual(float(result['fine'].amount), expected_fine)

    def test_return_book_not_issued(self):
        """Test return of book that's not currently issued."""
        self.book_item1.status = BookStatus.AVAILABLE
        self.book_item1.save()

        result = LoanService.return_book(self.book_item1, self.member)

        self.assertFalse(result['success'])
        self.assertIn('not currently issued', result['message'])

    def test_return_book_wrong_member(self):
        """Test return of book by wrong member."""
        # Create a loan for a different member
        other_member = Member.objects.create_member(
            email='other@test.com',
            name='Other Member',
            phone='0987654321',
            password='password123'
        )

        loan = Loan.objects.create(
            member=other_member,
            book_item=self.book_item1,
            issue_date=timezone.now().date() - timedelta(days=5),
            due_date=timezone.now().date() + timedelta(days=5)
        )
        self.book_item1.mark_issued(due_date=loan.due_date)

        # Try to return as the wrong member
        result = LoanService.return_book(self.book_item1, self.member)

        self.assertFalse(result['success'])
        self.assertIn('did not borrow', result['message'])

    def test_reserve_book_success(self):
        """Test book reservation creates a waiting reservation."""
        result = LoanService.reserve_book(self.member, self.book1)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['reservation'])

        reservation = result['reservation']
        self.assertEqual(reservation.book, self.book1)
        self.assertEqual(reservation.member, self.member)
        self.assertEqual(reservation.status, ReservationStatus.WAITING)

    def test_reserve_book_duplicate(self):
        """Test duplicate reservation is rejected."""
        # Create first reservation
        LoanService.reserve_book(self.member, self.book1)

        # Try to reserve again
        result = LoanService.reserve_book(self.member, self.book1)

        self.assertFalse(result['success'])
        self.assertIn('already have a reservation', result['message'])

    def test_issue_book_fulfills_reservations(self):
        """Test that issuing a book fulfills pending reservations."""
        # Create a reservation first
        LoanService.reserve_book(self.member, self.book1)

        # Issue the book
        result = LoanService.issue_book(self.member, self.book_item1)

        self.assertTrue(result['success'])

        # Verify reservation is fulfilled
        reservation = Reservation.objects.filter(book=self.book1, member=self.member).first()
        if not reservation:
            self.fail("Expected a reservation to exist for the member and book.")
        self.assertEqual(reservation.status, ReservationStatus.COMPLETED)

    def test_issue_book_invalid_member(self):
        """Test issue with None member."""
        result = LoanService.issue_book(None, self.book_item1)

        self.assertFalse(result['success'])
        self.assertIn('Member not found', result['message'])

    def test_issue_book_invalid_book_item(self):
        """Test issue with None book item."""
        result = LoanService.issue_book(self.member, None)

        self.assertFalse(result['success'])
        self.assertIn('Book item not found', result['message'])

    def test_return_book_invalid_book_item(self):
        """Test return with None book item."""
        result = LoanService.return_book(None, self.member)

        self.assertFalse(result['success'])
        self.assertIn('Book item not found', result['message'])

    def test_return_book_invalid_member(self):
        """Test return with None member."""
        result = LoanService.return_book(self.book_item1, None)

        self.assertFalse(result['success'])
        self.assertIn('Member not found', result['message'])

