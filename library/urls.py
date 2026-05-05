from django.urls import path
from .views import index, add_book, view_members


urlpatterns = [
    path("", index, name="index"),
    path("add_book/", add_book, name="add_book"),
    path("view_members/", view_members, name="view_members"),
]