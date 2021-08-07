from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError('The User Must Provide Email-ID')

        if not username:
            raise ValueError('The User Must Provide Username')

        user = self.model(
            email=self.normalize_email(email), # It converts letters to lower case if uppercase is provided
            username=username,
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password):
        user = self.create_user(
            email=self.normalize_email(email), 
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50, help_text='Enter First Name')
    last_name = models.CharField(max_length=50, help_text='Enter Last Name')
    phone_number = models.CharField(max_length=10, help_text='Enter Contact Number')
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True, help_text='Enter Email Address')

    # Required Fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager() # To set our custom account manager as base manager

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self) -> str:
        return f'{self.email} - {self.first_name} {self.last_name}'

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='userprofile')

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'