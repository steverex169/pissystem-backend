
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.urls import reverse
from django.db import models
from django_rest_passwordreset.signals import reset_password_token_created
# from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from helpers.mail import send_mail

# Create your models here.
OPTIONS = (
    ('admin', 'Admin'),
    ('organization', 'Organization'),
    ('database-admin', 'Database Admin'),
    ('organization', 'Organization'),
)

class UserAccount(AbstractUser):
    email = models.EmailField(max_length=70, blank=True, null=True, unique=False)
    account_type = models.CharField(
    max_length=100, choices=OPTIONS, default='admin', blank=True, null=False)
    is_active = models.BooleanField(default=0, blank=False, null=True)
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    password_foradmins = models.CharField(max_length=1000, blank=True, null=False)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    subject, from_email, to = 'Password Reset', settings.EMAIL_HOST_USER, reset_password_token.user.email
    reset_password_link = settings.LINK_OF_REACT_APP + \
        "/" + reset_password_token.key + "/confirm-password"

    data = {
        'user': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_link': reset_password_link,
    }

    send_mail(subject, "forget-password-mail.html", from_email, to, data)
