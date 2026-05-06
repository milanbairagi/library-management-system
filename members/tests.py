from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

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

    def test_member_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "New Member",
                "email": "newmember@example.com",
                "phone": "5555555555",
                "password": "newmemberpass",
                "password2": "newmemberpass",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Member.objects.filter(email="newmember@example.com").exists())
        self.assertContains(response, "Login")

    def test_member_login_and_librarian_login(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.member.email, "password": self.member_password},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Member Dashboard")

        self.client.logout()
        response = self.client.post(
            reverse("login"),
            {"email": self.librarian.email, "password": self.librarian_password},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Librarian Dashboard")

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
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
