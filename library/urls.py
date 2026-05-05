from django.urls import path
from .views import add_book, index


urlpatterns = [
    path("", index, name="index"),
    path("add_book/", add_book, name="add_book"),
]