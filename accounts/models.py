from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class UserType(models.TextChoices):
        MEMBER = "member", _("Community Member")
        INVESTOR = "investor", _("Investor")
        STARTUP = "startup", _("Startup / Founder")
        COFOUNDER = "cofounder", _("Co-Founder")
        INCUBATOR = "incubator", _("Startup Incubator")
        REVOPS = "revops", _("Revenue Operations")
        CTO = "cto", _("CTO / Technical Lead")
        ADMIN = "admin", _("Admin")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # Override username field
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.URLField(max_length=500, blank=True, null=True)
    role = models.CharField(max_length=100, default='Developer')
    bio = models.TextField(blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.MEMBER
    )

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # authentication config
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.user_type})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"