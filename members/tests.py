from django.test import TestCase
from django.urls import reverse

from .models import Member


class MemberAndLibrarianAuthTests(TestCase):
    def setUp(self):
        self.member_password = "member-pass-123"
        self.librarian_password = "librarian-pass-123"
        self.member = Member.objects.create_member(
            email="member@example.com",
            name="Member User",
            phone="1234567890",
            password=self.member_password,
        )
        self.librarian = Member.objects.create_librarian(
            email="librarian@example.com",
            name="Librarian User",
            phone="9876543210",
            password=self.librarian_password,
        )

    def test_member_login_only_allows_non_staff_user(self):
        response = self.client.post(
            reverse("member_login"),
            {"email": self.member.email, "password": self.member_password},
            follow=True,
        )
        self.assertContains(response, "Member Dashboard")

        self.client.logout()
        response = self.client.post(
            reverse("member_login"),
            {"email": self.librarian.email, "password": self.librarian_password},
            follow=True,
        )
        self.assertContains(response, "not allowed to sign in as Member")

    def test_librarian_login_only_allows_staff_user(self):
        response = self.client.post(
            reverse("librarian_login"),
            {"email": self.librarian.email, "password": self.librarian_password},
            follow=True,
        )
        self.assertContains(response, "Librarian Dashboard")

        self.client.logout()
        response = self.client.post(
            reverse("librarian_login"),
            {"email": self.member.email, "password": self.member_password},
            follow=True,
        )
        self.assertContains(response, "not allowed to sign in as Librarian")

    def test_dashboard_routes_by_is_staff_flag(self):
        self.client.login(email=self.member.email, password=self.member_password)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Member Dashboard")

        self.client.logout()
        self.client.login(email=self.librarian.email, password=self.librarian_password)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Librarian Dashboard")

    def test_public_librarian_registration_is_disabled(self):
        response = self.client.get(reverse("librarian_register"))
        self.assertEqual(response.status_code, 403)
