from django.urls import path

from .views import (
    dashboard,
    login_for_role,
    librarian_register,
    logout_view,
    member_register,
)

urlpatterns = [
    path("login/", login_for_role, name="login"),
    path("register/", member_register, name="register"),
    path("register/librarian/", librarian_register, name="librarian_register"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
]
