from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'client')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    ROLE_CHOICES = (
        ('client', 'client'),
        ('supplier', 'supplier'),
        ('admin', 'admin'),
    )

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client', verbose_name='Роль')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Доступ к админке')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"


class Contact(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Пользователь'
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address_city = models.CharField(max_length=255, verbose_name='Город')
    address_street = models.CharField(max_length=255, verbose_name='Улица')
    address_house = models.CharField(max_length=50, verbose_name='Дом')
    address_building = models.CharField(max_length=50, blank=True, verbose_name='Корпус')
    address_structure = models.CharField(max_length=50, blank=True, verbose_name='Строение')
    address_apartment = models.CharField(max_length=50, blank=True, verbose_name='Квартира')

    class Meta:
        verbose_name = 'контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['-id']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.phone}"


class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='email_tokens',
        verbose_name='Пользователь'
    )
    code = models.CharField(max_length=64, unique=True, verbose_name='Код подтверждения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    expires_at = models.DateTimeField(verbose_name='Дата истечения')

    class Meta:
        verbose_name = 'токен подтверждения email'
        verbose_name_plural = 'Токены подтверждения email'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.code}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_expired

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = secrets.token_urlsafe(32)[:64]
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
