from django.core.management.base import BaseCommand
from books.models import Book, BookItem


class Command(BaseCommand):
    help = 'Seed the database with sample books and book items'

    def handle(self, *args, **kwargs):
        # Sample book data
        books_data = [
            {
                'isbn': '9783161484100',
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'publisher': 'Scribner',
                'subject': 'Fiction'
            },
            {
                'isbn': '9783161483334',
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'publisher': 'J.B. Lippincott & Co.',
                'subject': 'Fiction'
            },
            {
                'isbn': '9783161484230',
                'title': '1984',
                'author': 'George Orwell',
                'publisher': 'Secker & Warburg',
                'subject': 'Dystopian'
            }
        ]

        for book_data in books_data:
            book, created = Book.objects.get_or_create(**book_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Book "{book.title}" created.'))
            else:
                self.stdout.write(self.style.WARNING(f'Book "{book.title}" already exists.'))

            # Create book items for each book
            for i in range(1, 4):  # Create 3 copies of each book
                barcode = f"{book.isbn}-{i}"
                book_item, item_created = BookItem.objects.get_or_create(
                    book=book,
                    barcode=barcode,
                    defaults={'rack_number': f'R{i}'}
                )
                if item_created:
                    self.stdout.write(self.style.SUCCESS(f'Book item with barcode "{barcode}" created.'))
                else:
                    self.stdout.write(self.style.WARNING(f'Book item with barcode "{barcode}" already exists.'))