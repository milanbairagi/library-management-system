from django.urls import path

from .views import (
    dashboard,
    librarian_login,
    librarian_register,
    logout_view,
    member_login,
    member_register,
)

urlpatterns = [
    path("login/member/", member_login, name="member_login"),
    path("register/member/", member_register, name="member_register"),
    path("login/librarian/", librarian_login, name="librarian_login"),
    path("register/librarian/", librarian_register, name="librarian_register"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
]
