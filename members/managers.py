from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_member(self, email, name, phone, password=None):
        return self.create_user(
            email=email,
            name=name,
            phone=phone,
            password=password,
            is_staff=False,
            is_superuser=False,
        )

    def create_librarian(self, email, name, phone, password):
        return self.create_user(
            email=email,
            name=name,
            phone=phone,
            password=password,
            is_staff=True,
            is_superuser=False,
        )

    def create_superuser(self, email, name, phone, password):
        return self.create_user(
            email=email,
            name=name,
            phone=phone,
            password=password,
            is_staff=True,
            is_superuser=True,
        )


class LibrarianManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_staff=True)

    def create_user(self, email, name, phone, password=None, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields.setdefault("is_superuser", False)
        return super().create_user(
            email=email,
            name=name,
            phone=phone,
            password=password,
            **extra_fields,
        )
