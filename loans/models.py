from django.db import models
from books.models import Book, BookItem
from members.models import Member


FINE_PER_DAY = 50

class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    book_item = models.ForeignKey(BookItem, on_delete=models.CASCADE, related_name='loans')

    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Loan issued on {self.issue_date} due on {self.due_date}"

    def calculate_fine(self):
        try:
            fine_obj = Fine.objects.get(loan=self)
        except Fine.DoesNotExist:
            fine_obj = None
        
        if fine_obj and not fine_obj.paid:
            return fine_obj.amount
        
        return 0


class Fine(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Fine for loan issued on {self.loan.issue_date} - Amount: {self.amount}"

    
    def calculate_fine(self, days_late: int):
        fine = days_late * FINE_PER_DAY
        return fine


    def pay_fine(self, amount):
        if amount >= self.amount:
            self.paid = True
            self.save()
            return True
        return False


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
        #TODO: Implement reservation cancellation logic
        pass