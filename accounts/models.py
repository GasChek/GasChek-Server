from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# from django.db.models.signals import post_save
# from functions.CustomQuery import generate_unique_code

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
        max_length=50, unique=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=1000, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    phonenumber = models.CharField(max_length=25, blank=True)
    state = models.CharField(max_length=25, blank=True)
    is_dealer = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None
    objects = CustomAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # @staticmethod
    # def create_device_model(sender, instance, created, **kwargs):
    #     if created:
    #         if (instance.is_dealer is False and instance.is_staff is False):
    #             device_id = generate_unique_code(Gaschek_Device)
    #             Gaschek_Device.objects.create(user=instance, device_id=device_id)


    def __str__(self):
        if self.is_staff:
            return f"{self.email} ADMIN"
        elif self.is_dealer:
            return f"{self.email} GAS DEALER"
        else:
            return f"{self.email} USER"
# post_save.connect(User.create_device_model, sender=User)


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return str(self.user)


class Gas_Dealer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=50)
    phonenumber = models.CharField(max_length=15)
    state = models.CharField(max_length=25)
    rating = models.CharField(max_length=10, blank=True)
    users_rate_count = models.CharField(max_length=10000, blank=True)
    users_rate_cummulation = models.CharField(max_length=10000, blank=True)
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
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

class Cylinder_Price(models.Model):
    gas_dealer = models.ForeignKey(Gas_Dealer, on_delete=models.CASCADE)
    cylinder = models.DecimalField(decimal_places=1, max_digits=10)
    price = models.IntegerField()

    class Meta:
        ordering = ['gas_dealer']

    def __str__(self):
        return f"{self.gas_dealer} {self.cylinder}kg NGN {self.price}"

class Delivery_Fee(models.Model):
    gas_dealer = models.ForeignKey(Gas_Dealer, on_delete=models.CASCADE)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.gas_dealer} delivery fee"

class Abandoned_Subaccounts(models.Model):
    company_name = models.CharField(max_length=50)
    #SUBACOUNT
    subaccount_code = models.CharField(max_length=100, blank=True)
    subaccount_id = models.BigIntegerField(blank=True)

    def __str__(self):
        return self.company_name