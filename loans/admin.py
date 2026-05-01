from django.contrib import admin
from .models import Fine, Loan, Reservation


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book_item', 'member', 'issue_date', 'due_date', 'return_date')
    search_fields = ('book_item__book__title', 'member__name')


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'paid')
    search_fields = ('loan__member__name',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'status', 'date')
    search_fields = ('book__title', 'member__name')