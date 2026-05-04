from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


User = get_user_model()


class MemberLibrarianBackend(ModelBackend):
    """Authenticate users by email from the single auth user model."""

    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        login_email = email or username
        if not login_email or not password:
            return None

        try:
            user = User.objects.get(email=login_email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
