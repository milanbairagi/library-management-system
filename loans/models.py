from django.db import models
from books.models import Book, BookItem
from members.models import Member
from decimal import Decimal


FINE_PER_DAY = 50

class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    book_item = models.ForeignKey(BookItem, on_delete=models.CASCADE, related_name='loans')

    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Loan issued on {self.issue_date} due on {self.due_date}"

    def calculate_and_create_fine(self):
        """Calculate fine amount and create/return Fine object if late return.
        
        Side effect: Creates Fine object in database if return_date > due_date.
        """
        try:
            fine_obj = Fine.objects.get(loan=self)
        except Fine.DoesNotExist:
            fine_obj = None

        # Calculate fine if the book is returned late and no fine has been created yet
        if not fine_obj and self.return_date and self.return_date > self.due_date:
            days_late = (self.return_date - self.due_date).days
            fine_amount = days_late * FINE_PER_DAY
            fine_obj = Fine.objects.create(loan=self, amount=fine_amount)
        
        return fine_obj
    
    def get_pending_fine(self):
        """Get pending fine amount without creating new fines."""
        try:
            fine_obj = Fine.objects.get(loan=self)
            if not fine_obj.fully_paid:
                return fine_obj.get_pending_amount()
        except Fine.DoesNotExist:
            pass
        return 0


class Fine(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Fine for loan issued on {self.loan.issue_date} - Amount: {self.amount}"

    @property
    def fully_paid(self):
        return self.paid or self.get_pending_amount() == 0
    
    def get_pending_amount(self):
        return float(self.amount) if not self.paid else 0

    def pay_fine(self, amount):
        """Record a fine payment (supports partial payments).
        
        Args:
            amount: Payment amount
            
        Returns:
            tuple: (success: bool, pending: float) - whether payment was recorded and pending amount
        """
        amount = float(amount)
        pending = self.get_pending_amount()
        
        if amount <= 0:
            return False, pending
        
        if amount >= pending:
            self.paid = True
            self.save()
            return True, 0
        else:
            # Partial payment
            self.amount -= Decimal(str(amount))
            self.save()
            return True, pending - amount


class ReservationStatus(models.TextChoices):
    WAITING = 'waiting', 'Waiting'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ReservationStatus.choices, default=ReservationStatus.WAITING)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Reservation for {self.book.title} by {self.member.name}"

    def cancel_reservation(self):
        self.status = ReservationStatus.CANCELLED
        self.save()