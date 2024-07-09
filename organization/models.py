from django.db import models
from account.models import UserAccount
# Create your models here.

class Organization(models.Model):
    account_id = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    user_name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='user name')
    email = models.EmailField(max_length=255, blank=False, null=True)
    country = models.CharField(max_length=255, blank=False, null=True)
    website = models.CharField(max_length=255, blank=False, null=True)
    registered_at = models.DateTimeField(
        max_length=255, null=True, blank=False)
    photo = models.ImageField(
        upload_to='organization', verbose_name='Organization\'s Photo', default="blank")
    def __str__(self):
        return self.name

        