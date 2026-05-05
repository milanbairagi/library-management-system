from django.urls import path
from .views import index, add_book, issue_book, view_members, return_book


urlpatterns = [
    path("", index, name="index"),
    path("add_book/", add_book, name="add_book"),
    path("view_members/", view_members, name="view_members"),
    path("issue_book/", issue_book, name="issue_book"),
    path("return_book/", return_book, name="return_book"),
]