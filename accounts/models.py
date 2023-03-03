from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
# Create your models here.


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_active", True)
        other_fields.setdefault("is_superuser", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')

        if other_fields.get("is_superuser") is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, password, **other_fields)

    def create_user(self, email, password, **other_fields):
        # if user_name is None:
        #     raise ValueError('Users must provide a username')
        if email is None:
            raise ValueError('Users must provide an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    email = models.EmailField(
        max_length=50, unique=True, null=True, blank=True)
    firstname = models.CharField(max_length=50, blank=True)
    lastname = models.CharField(max_length=50, blank=True)
    usernames = models.CharField(
        max_length=50, unique=True, null=True, blank=True)
    address = models.CharField(max_length=1000, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    phonenumber_ordering = models.CharField(max_length=25, blank=True)
    phonenumber_gaschek_device_1 = models.CharField(max_length=25, blank=True)
    phonenumber_gaschek_device_2 = models.CharField(max_length=25, blank=True)
    phonenumber_gaschek_device_3 = models.CharField(max_length=25, blank=True)
    state = models.CharField(max_length=25, blank=True)
    is_dealer = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None
    objects = CustomAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['usernames']

    @staticmethod
    def create_device_model(sender, instance, created, **kwargs):
        if created:
            if (instance.is_dealer is False and instance.is_staff is False):
                Gaschek_Device.objects.create(user=instance)

    def __str__(self):
        if self.is_staff:
            return "{} ADMIN".format(self.email)
        if self.is_dealer:
            return "{}".format(self.email)
        if self.is_dealer is False:
            return "{}".format(self.usernames)


post_save.connect(User.create_device_model, sender=User)


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return str(self.user)


class Gaschek_Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choices = {
        ("on", "on"),
        ("off", "off")
    }
    alarm = models.CharField(choices=choices, max_length=10, default="off")
    call = models.CharField(choices=choices, max_length=10, default="off")
    text = models.CharField(choices=choices, max_length=10, default="off")
    cylinder = models.CharField(max_length=10, default="0kg")
    gas_mass = models.FloatField(max_length=10, default="0")
    gas_level = models.IntegerField(default=0)
    battery_level = models.IntegerField(default=0)
        
    def __str__(self):
        return "{} Device".format(self.user.usernames)


class Gas_Dealer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=50)
    phonenumber = models.CharField(max_length=15, unique=True)
    state = models.CharField(max_length=25)
    rating = models.CharField(max_length=10)
    users_rate_count = models.CharField(max_length=10000)
    users_rate_cummulation = models.CharField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    selling = models.BooleanField(default=True)
    open = models.BooleanField(default=False)
    sold = models.BigIntegerField(default=0)
    #LOCATION
    longitude = models.CharField(max_length=500)
    latitude = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    #SUBACOUNT
    account_number = models.CharField(max_length=30)
    bank_name = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=5)
    percentage_charge = models.DecimalField(blank=True, decimal_places=1, max_digits=4)
    subaccount_code = models.CharField(max_length=100, blank=True)
    subaccount_id = models.BigIntegerField(blank=True)

    def __str__(self):
        return self.company_name

class Abandoned_Subaccounts(models.Model):
    company_name = models.CharField(max_length=50)
    #SUBACOUNT
    subaccount_code = models.CharField(max_length=100, blank=True)
    subaccount_id = models.BigIntegerField(blank=True)

    def __str__(self):
        return self.company_name